/* global django, jQuery */
(function ($) {
    if (!$) {
        $ = window.jQuery; // One last try using global jQuery
    }

    console.log('Admin Order JS Loaded - v6 (Dynamic Units). jQuery:', $ ? 'Found' : 'Missing');

    if (!$) {
        console.error('jQuery not found! Auto-price script will not work.');
        return;
    }

    $(document).ready(function () {
        console.log('Document Ready. Attaching listeners.');

        // Store delivery charge
        var deliveryCharge = 0;

        // Fetch delivery charge on load
        $.ajax({
            url: '/api/delivery-charges/',
            type: 'GET',
            success: function (data) {
                if (data && data.amount) {
                    deliveryCharge = parseFloat(data.amount);
                    console.log('Delivery Charge Loaded:', deliveryCharge);
                    calculateTotal(); // Recalculate once loaded
                }
            },
            error: function (err) {
                console.error("Failed to load delivery charges", err);
            }
        });

        // Function to calculate and update total
        function calculateTotal() {
            var total = 0;
            // Iterate over all inline items (excluding empty template)
            // We use attribute selectors because Jazzmin or other themes might change class nesting
            $('.inline-related').not('.empty-form').each(function () {
                var row = $(this);

                // Also check for hidden delete checkbox. If checked, don't include in total.
                // Selector: input ending with -DELETE
                var deleteInput = row.find('input[name$="-DELETE"]');
                if (deleteInput.length && deleteInput.is(':checked')) {
                    return; // continue
                }

                // Find Quantity and Price 
                var quantityInput = row.find('input[name$="-quantity"]');
                var priceInput = row.find('input[name$="-price_at_purchase"]');

                var qty = parseFloat(quantityInput.val()) || 0;
                var price = parseFloat(priceInput.val()) || 0;

                console.log(`Row Item: Qty=${qty}, Price=${price}`);

                total += qty * price;
            });

            console.log('Items Total:', total);

            // Add delivery charge
            total += deliveryCharge;

            console.log('Calculated Total (inc. Delivery):', total);

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
                    if (data) {
                        // Dynamic Unit Type Logic
                        var $unitSelect = $row.find('select[name$="-unit_type"]');
                        if ($unitSelect.length) {
                            // Reset options first
                            $unitSelect.find('option').prop('disabled', false).show();

                            // Disable Pack if not available
                            if (!data.pack_price) {
                                // Select2 might need rebuilding, but standard hide on option works for many
                                // For Select2, we often need to clear selection if it was selected
                                var $packOpt = $unitSelect.find('option[value="Pack"]');
                                $packOpt.prop('disabled', true).hide();

                                if ($unitSelect.val() === 'Pack') {
                                    $unitSelect.val('Unit').trigger('change');
                                    // Prevent double calc as trigger change calls this function again partially
                                    return;
                                }
                            }

                            // Disable Strip if not available
                            if (!data.strip_price) {
                                var $stripOpt = $unitSelect.find('option[value="Strip"]');
                                $stripOpt.prop('disabled', true).hide();

                                if ($unitSelect.val() === 'Strip') {
                                    $unitSelect.val('Unit').trigger('change');
                                    return;
                                }
                            }

                            // Refresh Select2 if present
                            if ($unitSelect.hasClass('select2-hidden-accessible')) {
                                // Jazzmin/Select2 specific: destroy and re-init might be overkill, 
                                // but triggering change.select2 usually updates display if underlying options change.
                                // Actually, disabling options is enough for native select, for Select2 verify:
                                $unitSelect.trigger('change.select2');
                            }
                        }

                        // Re-fetch unit type after potential reset
                        var currentUnit = 'Unit';
                        if ($unitSelect.length) {
                            currentUnit = $unitSelect.val();
                        }

                        var price = 0;
                        if (currentUnit === 'Pack' && data.pack_price) {
                            price = parseFloat(data.pack_price);
                        } else if (currentUnit === 'Strip' && data.strip_price) {
                            price = parseFloat(data.strip_price);
                        } else {
                            price = parseFloat(data.price);
                        }

                        var $priceInput = $row.find('input[name$="-price_at_purchase"]');
                        $priceInput.val(price);

                        // Visual feedback
                        $priceInput.css('background-color', '#e8f0fe');
                        setTimeout(function () { $priceInput.css('background-color', ''); }, 500);

                        // Recalculate total after price update
                        calculateTotal();

                        // Store product data on the row for future unit changes
                        $row.data('product-data', data);
                    }
                },
                error: function (xhr, status, error) {
                    console.error('API Error:', error);
                }
            });
        }

        // --- Event Binding for Backend Authority Logic ---

        // Helper to reset manual flag
        function setManualFlag($row, isManual) {
            var $manualInput = $row.find('input[name$="-is_manual_price"]');
            $manualInput.prop('checked', isManual);
            // Also update value attribute for robustness (though checkbox state usually suffices)
            if (isManual) {
                $manualInput.attr('checked', 'checked');
            } else {
                $manualInput.removeAttr('checked');
            }
            console.log("Manual Flag set to:", isManual, "for row", $row.attr('id'));
        }

        // 1. Creation/Selection of Product -> Auto Calc (Manual = False)
        $('body').on('select2:select change', '.admin-autocomplete', function (e) {
            var $row = $(this).closest('.inline-related');
            setManualFlag($row, false);
            fetchAndSetPrice($(this));
        });

        // 2. Select2 Wrapper fallback -> Auto Calc (Manual = False)
        $('body').on('select2:select', '.field-product', function (e) {
            var $select = $(e.target).find('select');
            if ($select.length === 0) $select = $(e.target);
            var $row = $select.closest('.inline-related');

            setManualFlag($row, false);

            if ($select.hasClass('admin-autocomplete')) {
                fetchAndSetPrice($select);
            }
        });

        // 3. Fallback for standard select changes -> Auto Calc (Manual = False)
        $('body').on('change', 'select[name$="-product"]', function (e) {
            var $row = $(this).closest('.inline-related');
            setManualFlag($row, false);
            fetchAndSetPrice($(this));
        });

        // 4. Unit Type Change -> Auto Calc (Manual = False)
        $('body').on('change select2:select', 'select[name$="-unit_type"]', function (e) {
            var $row = $(this).closest('.inline-related');
            setManualFlag($row, false);

            // Re-run price logic using cache
            var data = $row.data('product-data');

            if (data) {
                // Use cached data
                var unitType = $(this).val();
                var price = 0;
                if (unitType === 'Pack' && data.pack_price) {
                    price = parseFloat(data.pack_price);
                } else if (unitType === 'Strip' && data.strip_price) {
                    price = parseFloat(data.strip_price);
                } else {
                    price = parseFloat(data.price);
                }

                var $priceInput = $row.find('input[name$="-price_at_purchase"]');
                $priceInput.val(price);
                // Force update attribute
                $priceInput.attr('value', price);

                // Visual feedback
                $priceInput.css('background-color', '#e8f0fe');
                setTimeout(function () { $priceInput.css('background-color', ''); }, 500);

                calculateTotal();
            } else {
                // Fetch data again if product is selected
                var $productSelect = $row.find('select[name$="-product"]');
                // Standard admin autocompletes are hidden selects
                if ($productSelect.length === 0) {
                    var $widget = $row.find('.admin-autocomplete');
                    if ($widget.length) {
                        fetchAndSetPrice($widget);
                        return;
                    }
                }
                if ($productSelect.val()) {
                    fetchAndSetPrice($productSelect);
                }
            }
        });

        // 5. MANUAL PRICE OVERRIDE DETECTION
        // If the user types in the price box, we flag it as manual.
        $('body').on('input change', 'input[name$="-price_at_purchase"]', function (e) {
            // We need to differentiate between JS setting value and User setting value.
            // 'input' event is best for user typing.
            // However, some JS might trigger 'change'.
            // Simplest heuristic: If this event was NOT triggered by our code (which we don't trigger explicit change on input usually), it's user.
            // But actually, we set .val().
            // .val() does NOT trigger 'input' event. So 'input' is safe for user typing.
            if (e.type === 'input') {
                var $row = $(this).closest('.inline-related');
                setManualFlag($row, true);
            }
        });

        // 6. User manually changes Quantity or Price
        $('body').on('change keyup', 'input[name$="-quantity"], input[name$="-price_at_purchase"]', function () {
            calculateTotal();
        });

        // 6. User deletes a row (click on remove button usually toggles a checkbox or removes DOM)
        $('body').on('click', '.inline-deletelink', function () {
            // Wait for DOM update
            setTimeout(calculateTotal, 200);
        });

        // 7. User checks the "Delete" checkbox in StackedInline
        $('body').on('change', 'input[name$="-DELETE"]', function () {
            calculateTotal();
        });

        // Initial calculation on load
        setTimeout(calculateTotal, 1000);
        setTimeout(calculateTotal, 3000); // Robustness

    });
})(typeof django !== 'undefined' ? django.jQuery : window.jQuery);
