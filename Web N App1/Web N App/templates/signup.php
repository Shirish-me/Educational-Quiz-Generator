<?php
// Database configuration
$servername = "localhost"; // Your database host
$username = "root"; // Your database username
$password = "shirish@2004"; // Your database password
$dbname = "signup_db"; // Your database name

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Handle signup form submission
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = $_POST['username'];
    $password = password_hash($_POST['password'], PASSWORD_DEFAULT); // Hash the password
    $role = $_POST['role'];
    $studentId = isset($_POST['studentId']) ? $_POST['studentId'] : null;
    $course = isset($_POST['course']) ? $_POST['course'] : null;
    $teacherId = isset($_POST['teacherId']) ? $_POST['teacherId'] : null;
    $subject = isset($_POST['subject']) ? $_POST['subject'] : null;

    // Prepare and bind
    $stmt = $conn->prepare("INSERT INTO Users (username, password, role, student_id, course, teacher_id, subject) VALUES (?, ?, ?, ?, ?, ?, ?)");
    $stmt->bind_param("sssssss", $username, $password, $role, $studentId, $course, $teacherId, $subject);

    // Execute the statement
    if ($stmt->execute()) {
        echo "New record created successfully";
    } else {
        echo "Error: " . $stmt->error;
    }

    // Close the statement and connection
    $stmt->close();
}
$conn->close();
?>
