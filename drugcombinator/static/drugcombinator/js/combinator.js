document.addEventListener('DOMContentLoaded', event => {

    const drugsSelector = document.getElementById('id_drugs_field');
    const submitBtn = document.getElementById('combine-submit');
    const drugsBtns = document.querySelectorAll('.drug.btn')

    function updateDrugsBtns() {

        drugsSelector.querySelectorAll('option').forEach(drugItem => {

            const drugBtn = document.getElementById('drug-' + drugItem.value);

            if (drugBtn != null) {
                var selected = drugItem.selected;
                if (drugBtn.classList.contains('selected') != selected) {
                    if (selected) {
                        drugBtn.classList.add('selected');
                    } else {
                        drugBtn.classList.remove('selected');
                    }
                }
            }
        });
    }

    function toggleSubmitBtn() {
        var selectedDrugs = 0;
        drugsSelector.querySelectorAll('option').forEach(drugItem => {
            if (drugItem.selected) selectedDrugs ++;
        })

        if (selectedDrugs < 2) {
            submitBtn.classList.add('disabled');
        } else {
            submitBtn.classList.remove('disabled');
        }
    }

    drugsSelector.querySelector('option[value=""]').disabled = true;
    M.FormSelect.init(drugsSelector);

    toggleSubmitBtn();
    drugsSelector.addEventListener('change', toggleSubmitBtn);
    
    updateDrugsBtns();
    drugsSelector.addEventListener('change', updateDrugsBtns);

    drugsBtns.forEach(drugBtn => {
        
        const drugId = drugBtn.id.replace('drug-', '');
        const drugItem = drugsSelector.querySelector(`option[value="${drugId}"]`);
        
        drugBtn.addEventListener('click', event => {
            
            var selected = !drugBtn.classList.contains('selected');
            if (selected) {
                drugBtn.classList.add('selected');
            } else {
                drugBtn.classList.remove('selected');
            }
            if (drugItem.selected != selected) {
                drugItem.selected = selected;
                M.FormSelect.init(drugsSelector);
            }

            toggleSubmitBtn();
        });
    });
});