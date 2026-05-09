document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector("form");

    const image1 = document.querySelector('input[name="image1"]');
    const image2 = document.querySelector('input[name="image2"]');

    form.addEventListener("submit", (e) => {

        if (!image1.files.length || !image2.files.length) {

            e.preventDefault();

            alert("Please upload both images");

            return;
        }

        const file1 = image1.files[0];
        const file2 = image2.files[0];

        const allowedTypes = ["image/jpeg", "image/png", "image/jpg"];

        if (
            !allowedTypes.includes(file1.type) ||
            !allowedTypes.includes(file2.type)
        ) {

            e.preventDefault();

            alert("Only JPG, JPEG, and PNG images are allowed");

            return;
        }

        const maxSize = 5 * 1024 * 1024;

        if (file1.size > maxSize || file2.size > maxSize) {

            e.preventDefault();

            alert("Image size must be below 5MB");

            return;
        }

    });

});