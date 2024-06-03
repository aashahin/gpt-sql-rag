const { spawn } = require('child_process');
const readline = require('readline');

// Function to call the Python script
function callPythonScript(question) {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python3', ['main.py', question]);

        pythonProcess.stdout.on('data', (data) => {
            resolve(data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
            reject(data.toString());
        });
    });
}

// Read user input from terminal
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

rl.question('Please enter your question: ', (question) => {
    callPythonScript(question)
        .then((response) => {
            console.log(response);
            rl.close();
        })
        .catch((error) => {
            console.error('Error:', error);
            rl.close();
        });
});
