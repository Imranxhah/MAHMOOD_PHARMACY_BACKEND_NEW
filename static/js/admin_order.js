
/* global django, jQuery */
(function ($) {
    if (!$) {
        $ = window.jQuery; // One last try using global jQuery
    }

    console.log('Admin Order JS Loaded - v4 (Total Calc). jQuery:', $ ? 'Found' : 'Missing');

    if (!$) {
        console.error('jQuery not found! Auto-price script will not work.');
        return;
    }

    $(document).ready(function () {
        console.log('Document Ready. Attaching listeners.');

        // Function to calculate and update total
        function calculateTotal() {
            var total = 0;
            // Iterate over all inline items (excluding empty template)
            $('.inline-related').not('.empty-form').each(function () {
                var row = $(this);
                // In stacked inline, fields are sometimes wrapped in div.field-X
                var quantityInput = row.find('.field-quantity input');
                var priceInput = row.find('.field-price_at_purchase input');

                // Also check for hidden delete checkbox. If checked, don't include in total.
                var deleteInput = row.find('.delete input[type=checkbox]');
                if (deleteInput.length && deleteInput.is(':checked')) {
                    return; // continue
                }

                var qty = parseFloat(quantityInput.val()) || 0;
                var price = parseFloat(priceInput.val()) || 0;

                total += qty * price;
            });

            console.log('Calculated Total:', total);

            // Update the Total Amount field (read-only div)
            var totalField = $('.field-total_amount .readonly');
            if (totalField.length) {
                totalField.text(total.toFixed(2));
                // Add a highlight effect
                totalField.css('color', 'green').css('font-weight', 'bold');
            }
        }

        function fetchAndSetPrice($select) {
            var val = $select.val();
            if (!val) return;

            var $row = $select.closest('.inline-related');
            if ($row.length === 0) $row = $select.closest('.form-row');

            $.ajax({
                url: '/api/products/' + val + '/',
                type: 'GET',
                success: function (data) {
                    if (data && data.price) {
                        var $priceInput = $row.find('.field-price_at_purchase input');
                        $priceInput.val(data.price);

                        // Visual feedback
                        $priceInput.css('background-color', '#e8f0fe');
                        setTimeout(function () { $priceInput.css('background-color', ''); }, 500);

                        // Recalculate total after price update
                        calculateTotal();
                    }
                },
                error: function (xhr, status, error) {
                    console.error('API Error:', error);
                }
            });
        }

        // --- Event Binding ---

        // 1. Creation/Selection of Product
        $('body').on('select2:select change', '.admin-autocomplete', function (e) {
            fetchAndSetPrice($(this));
        });

        // 2. Select2 Wrapper fallback
        $('body').on('select2:select', '.field-product', function (e) {
            var $select = $(e.target).find('select');
            if ($select.length === 0) $select = $(e.target);
            if ($select.hasClass('admin-autocomplete')) {
                fetchAndSetPrice($select);
            }
        });

        // 3. User manually changes Quantity or Price
        $('body').on('change keyup', '.field-quantity input, .field-price_at_purchase input', function () {
            calculateTotal();
        });

        // 4. User deletes a row (click on remove button usually toggles a checkbox or removes DOM)
        $('body').on('click', '.inline-deletelink', function () {
            // Wait for DOM update
            setTimeout(calculateTotal, 200);
        });

        // 5. User checks the "Delete" checkbox in StackedInline
        $('body').on('change', '.delete input[type=checkbox]', function () {
            calculateTotal();
        });

        // Initial calculation on load
        setTimeout(calculateTotal, 1000);

    });
})(typeof django !== 'undefined' ? django.jQuery : window.jQuery);
