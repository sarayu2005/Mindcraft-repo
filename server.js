// server.js
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt'); // For password security
const bodyParser = require('body-parser');
const nodemailer = require('nodemailer');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(bodyParser.json());
app.use(express.static('public')); // Serves your HTML files

// --- DATABASE SETUP ---
const db = new sqlite3.Database('./users.db', (err) => {
    if (err) console.error(err.message);
    console.log('Connected to the SQLite database.');
});

// Create Users Table if it doesn't exist
db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)`);

// --- EMAIL SETUP ---
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: 'valtetisarayu@gmail.com', // REPLACE THIS
        pass: 'tiju hcvp yqwa xytf'      // REPLACE THIS (Not your login password)
    }
});

// --- ROUTES ---

// 1. Registration Route
app.post('/register', async (req, res) => {
    const { email, password } = req.body;

    try {
        // Hash the password (security best practice)
        const hashedPassword = await bcrypt.hash(password, 10);

        const sql = `INSERT INTO users (email, password) VALUES (?, ?)`;
        db.run(sql, [email, hashedPassword], function(err) {
            if (err) {
                return res.status(400).json({ error: 'User already exists or invalid data' });
            }
            res.status(200).send('User created successfully');
        });
    } catch (e) {
        res.status(500).send('Server error');
    }
});

// 2. Login Route
app.post('/login', (req, res) => {
    const { email, password } = req.body;

    const sql = `SELECT * FROM users WHERE email = ?`;
    db.get(sql, [email], async (err, user) => {
        if (err) return res.status(500).send('Server error');
        if (!user) return res.status(400).send('User not found');

        // Check password
        const match = await bcrypt.compare(password, user.password);
        if (match) {
            // --- SEND SUCCESS EMAIL ---
            const mailOptions = {
                from: 'Mindcraft System',
                to: email,
                subject: 'Login Successful - Mindcraft',
                text: `Hello,\n\nYou have successfully logged into Mindcraft.\n\nWelcome back!`
            };

            transporter.sendMail(mailOptions, (error, info) => {
                if (error) {
                    console.log('Email error:', error);
                    // We still allow login even if email fails, but log it
                } else {
                    console.log('Email sent: ' + info.response);
                }
            });

            res.status(200).send('Login successful');
        } else {
            res.status(400).send('Invalid password');
        }
    });
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});