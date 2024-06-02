// This code adds a click event listener to the 'mobile-menu-button' element in the navigation bar.
// When the button is clicked, it toggles the 'hidden' class on the 'mobile-menu' element.
document
  .getElementById("mobile-menu-button")
  .addEventListener("click", function () {
    const menu = document.getElementById("mobile-menu");
    menu.classList.toggle("hidden");
  });

//  Hero section animation
document.addEventListener("DOMContentLoaded", function () {
  const slides = document.querySelectorAll(".hero-slide");
  let currentSlide = 0;
  function showSlide(index) {
    slides.forEach((slide, i) => {
      slide.classList.toggle("opacity-100", i === index);
      slide.classList.toggle("opacity-0", i !== index);
    });
  }

  function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
  }

  setInterval(nextSlide, 4000);
});

// Card Animation

document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".card-enter");
  cards.forEach((card, index) => {
    setTimeout(() => {
      card.classList.add("card-enter-active");
    }, index * 200); // Stagger the animations
  });
});

// Toggle Password Visibility
document.addEventListener("DOMContentLoaded", function () {
  const passwordField = document.getElementById("password");
  const confirmPasswordField = document.getElementById("confirm_password");
  const togglePassword = document.getElementById("togglePassword");
  const toggleConfirmPassword = document.getElementById(
    "toggleConfirmPassword",
  );

  togglePassword.addEventListener("click", function () {
    const type = passwordField.type === "password" ? "text" : "password";
    passwordField.type = type;
    this.querySelector("i").classList.toggle("fa-eye");
    this.querySelector("i").classList.toggle("fa-eye-slash");
  });

  toggleConfirmPassword.addEventListener("click", function () {
    const type = confirmPasswordField.type === "password" ? "text" : "password";
    confirmPasswordField.type = type;
    this.querySelector("i").classList.toggle("fa-eye");
    this.querySelector("i").classList.toggle("fa-eye-slash");
  });
});

// script for the dashboard_base html

// Toggle Sidebar
const hamburger = document.getElementById('hamburger');
const sidebar = document.getElementById('sidebar');
hamburger.addEventListener('click', () => {
    sidebar.classList.toggle('sidebar-closed');
});

// Toggle User Menu
const userMenuButton = document.getElementById('user-menu-button');
const userMenu = document.getElementById('user-menu');
userMenuButton.addEventListener('click', () => {
    userMenu.classList.toggle('hidden');
});

// Close User Menu on Click Outside
window.addEventListener('click', (e) => {
    if (!userMenuButton.contains(e.target) && !userMenu.contains(e.target)) {
        userMenu.classList.add('hidden');
    }
});
