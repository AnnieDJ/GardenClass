// email_validation.js

document.getElementById('email').addEventListener('blur', function() {
    var email = this.value;
    var emailMessage = document.getElementById('emailMessage');

    // Regular expression to validate email format
    var emailPattern = /[^@]+@[^@]+\.[^@]+$/;

    if (!emailPattern.test(email)) {
        // If email format is invalid, display an error message
        emailMessage.textContent = 'Invalid email format';
        emailMessage.style.color = 'red';
    } else {
        // If email format is valid, clear the error message
        emailMessage.textContent = '';

        // Check if the email is changed
        if (this.defaultValue === email) {
            // If email is not changed, display a success message
            emailMessage.textContent = 'Email is valid';
            emailMessage.style.color = 'green';
            // Optionally, change the styling to indicate validity
            document.getElementById('email').classList.remove('invalid');
            document.getElementById('email').classList.add('valid');
        } else {
            // If email is changed, send an asynchronous request to check uniqueness
            fetch('/check_email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'email=' + encodeURIComponent(email)
            })
            .then(response => response.json())
            .then(data => {
                // Handle response from the server
                if (data.valid) {
                    // Email is valid
                    // Display a success message
                    emailMessage.textContent = 'Email is valid';
                    emailMessage.style.color = 'green';
                    // Optionally, change the styling to indicate validity
                    document.getElementById('email').classList.remove('invalid');
                    document.getElementById('email').classList.add('valid');
                } else {
                    // Email is not valid
                    // Display an error message
                    emailMessage.textContent = 'Email is already in use';
                    emailMessage.style.color = 'red';
                    // Optionally, change the styling to indicate invalidity
                    document.getElementById('email').classList.remove('valid');
                    document.getElementById('email').classList.add('invalid');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    }
});
