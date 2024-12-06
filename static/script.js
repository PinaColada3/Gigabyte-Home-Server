let mailP = document.getElementById("mail_opened");

console.log("Hello, World!");
console.log(mailP.textContent);

function reset() {
fetch('/api/mail-emptied', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ command: 'SET' })
})
.then(response => response.json())
.then(data => {
    console.log('Success:', data);
})
.catch((error) => {
    console.error('Error:', error);
});
    mailP.textContent = "Test";
}