document.addEventListener('DOMContentLoaded', event => {
    const drugsBtns = document.querySelectorAll('.drug-selector .btn');
    const interCards = document.querySelectorAll('.interaction-content');

    drugsBtns.forEach(drugBtn => {
        const drugId = drugBtn.id.replace('drug-', '');

        drugBtn.addEventListener('click', event => {
            drugsBtns.forEach(drugBtn => {
                drugBtn.classList.remove('selected');
            });
            drugBtn.classList.add('selected');
            
            const interCard = document.getElementById('card-' + drugId);
            interCards.forEach(interCard => {
                interCard.style.display = 'none';
            })
            interCard.style.display = 'initial';
        });
    });

    interCards.forEach(interCard => {
        interCard.style.display = 'none';
    })
});