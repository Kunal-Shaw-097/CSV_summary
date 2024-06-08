document.addEventListener('DOMContentLoaded', function() {
    const xSelect = document.getElementById('id_column_x');
    const ySelect = document.getElementById('id_column_y');

    function updateOptions() {
        const selectedX = xSelect.value;
        const selectedY = ySelect.value;

        // Reset options
        [...xSelect.options].forEach(option => option.style.display = 'block');
        [...ySelect.options].forEach(option => option.style.display = 'block');

        // Hide selected y option in x select
        if (selectedY) {
            xSelect.querySelector(`option[value="${selectedY}"]`).style.display = 'none';
        }

        // Hide selected x option in y select
        if (selectedX) {
            ySelect.querySelector(`option[value="${selectedX}"]`).style.display = 'none';
        }
    }

    xSelect.addEventListener('change', updateOptions);
    ySelect.addEventListener('change', updateOptions);

    // Initial call to set up the correct options
    updateOptions();
});