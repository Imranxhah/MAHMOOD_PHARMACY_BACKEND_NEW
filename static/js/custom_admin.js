
// Custom Admin JS

document.addEventListener("DOMContentLoaded", function () {
    console.log("Custom Admin JS loaded");

    // Function to force full width on Select2 containers for mobile
    function fixSelect2Width() {
        if (window.innerWidth <= 991) {
            // Target all select2 containers
            var select2s = document.querySelectorAll('.select2-container');
            select2s.forEach(function (el) {
                el.style.setProperty('width', '100%', 'important');
                el.style.display = 'block';
            });

            // Also force standard inputs just in case
            var inputs = document.querySelectorAll('#content-main form input, #content-main form select');
            inputs.forEach(function (el) {
                if (el.type !== 'checkbox' && el.type !== 'radio' && el.type !== 'hidden') {
                    el.style.setProperty('width', '100%', 'important');
                }
            });


        }
    }

    // Run on load
    fixSelect2Width();

    // Run on resize
    window.addEventListener('resize', fixSelect2Width);

    // Run periodically to catch dynamically added widgets (e.g. inlines)
    setInterval(fixSelect2Width, 1000);
});
