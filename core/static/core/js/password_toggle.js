// Toggle Password Visibility
document.addEventListener('DOMContentLoaded', function () {
  const passwordField = document.getElementById('password');
  const confirmPasswordField = document.getElementById('confirm_password');
  const togglePassword = document.getElementById('togglePassword');
  const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');

  togglePassword.addEventListener('click', function () {
    const type = passwordField.type === 'password' ? 'text' : 'password';
    passwordField.type = type;
    this.querySelector('i').classList.toggle('fa-eye');
    this.querySelector('i').classList.toggle('fa-eye-slash');
  });

  toggleConfirmPassword.addEventListener('click', function () {
    const type = confirmPasswordField.type === 'password' ? 'text' : 'password';
    confirmPasswordField.type = type;
    this.querySelector('i').classList.toggle('fa-eye');
    this.querySelector('i').classList.toggle('fa-eye-slash');
  });
});