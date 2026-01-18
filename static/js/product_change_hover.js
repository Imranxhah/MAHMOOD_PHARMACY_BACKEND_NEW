document.addEventListener("DOMContentLoaded", function () {
    // Target the "Currently: <a href...>" link in file upload widgets
    const fileLinks = document.querySelectorAll('.file-upload a');

    fileLinks.forEach(link => {
        // Only process image links
        const href = link.getAttribute('href');
        if (!href || !href.match(/\.(jpeg|jpg|gif|png|webp)$/i)) {
            return;
        }

        // Create the wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'image-preview-container';
        wrapper.style.display = 'inline-block'; // Keep it inline with text

        // Create backdrop and popup
        const backdrop = document.createElement('div');
        backdrop.className = 'image-backdrop';

        const popup = document.createElement('div');
        popup.className = 'image-popup';

        const img = document.createElement('img');
        img.src = href;
        popup.appendChild(img);

        // Move the link inside the wrapper
        link.parentNode.insertBefore(wrapper, link);
        wrapper.appendChild(link);

        // Append popup elements to wrapper
        wrapper.appendChild(backdrop);
        wrapper.appendChild(popup);
    });
});
