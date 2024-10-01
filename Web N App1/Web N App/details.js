const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql');

const app = express();
app.use(bodyParser.urlencoded({ extended: true }));

// Create a connection to the database
const db = mysql.createConnection({
    host: 'localhost',
    user: 'your_username',
    password: 'your_password',
    database: 'your_database'
});

// Handle signup form submission
app.post('/signup', (req, res) => {
    const { username, password, role, studentId, course, teacherId, subject } = req.body;

    // Define the SQL query based on role
    let sql;
    if (role === 'student') {
        sql = 'INSERT INTO students (username, password, studentId, course) VALUES (?, ?, ?, ?)';
        db.query(sql, [username, password, studentId, course], (err) => {
            if (err) throw err;
            res.send('Student signed up successfully!');
        });
    } else if (role === 'teacher') {
        sql = 'INSERT INTO teachers (username, password, teacherId, subject) VALUES (?, ?, ?, ?)';
        db.query(sql, [username, password, teacherId, subject], (err) => {
            if (err) throw err;
            res.send('Teacher signed up successfully!');
        });
    }
});

// Start the server
app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
