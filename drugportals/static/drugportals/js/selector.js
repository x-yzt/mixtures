const mobileQueryString = '(max-width: 600px)';
const mobileScrollOffset = 70;


document.addEventListener('DOMContentLoaded', event => {
    const hashDrugSlug = window.location.hash.replace('#', '');
    const hashDrugBtn = document.getElementById('drug-' + hashDrugSlug);
    const hashInterCard = document.getElementById('card-' + hashDrugSlug);

    const drugsBtns = document.querySelectorAll('.drug-selector .btn');
    const interCards = document.querySelectorAll('.interaction-content');

    function reset_selector() {
        drugsBtns.forEach(drugBtn => {
            drugBtn.classList.remove('selected');
        });
        interCards.forEach(interCard => {
            interCard.style.display = 'none';
        })
    }

    drugsBtns.forEach(drugBtn => {
        const drugSlug = drugBtn.id.replace('drug-', '');
        const interCard = document.getElementById('card-' + drugSlug);

        drugBtn.addEventListener('click', event => {
            reset_selector();            
            drugBtn.classList.add('selected');
            interCard.style.display = 'initial';
            
            if (window.matchMedia(mobileQueryString).matches) {
                window.scrollTo({
                    top: interCard.getBoundingClientRect().top 
                        + window.scrollY
                        - mobileScrollOffset,
                    behavior: 'smooth',
                });
            }
            
            window.history.pushState({}, null, '#' + drugSlug);
        });
    });

    reset_selector();
    if (hashDrugBtn) {
        hashDrugBtn.classList.add('selected');
        hashInterCard.style.display = 'initial';
    } else {
        // Strips invalid anchor tag
        window.history.replaceState({}, null, window.location.pathname);
    }
});