document.addEventListener('DOMContentLoaded', event => {
    const btns = document.querySelectorAll('.modal-trigger[id^="contrib-"');
    const modal = document.querySelector('#contrib-modal');
    const topic = modal.querySelector('#contrib-topic');
    const form = modal.querySelector('form');
    const field = modal.querySelector('#id_interaction_field');
    const submit = modal.querySelector('button[type="submit"]');
    const progress = modal.querySelector('.progress');
    
    btns.forEach(btn => {
        const interactionId = btn.id.replace('contrib-', '');
        const interactionName = 
            btn.closest('.interaction').getAttribute('data-interaction-name');

        btn.addEventListener('click', event => {
            field.value = interactionId;
            topic.textContent = interactionName;
        });
    });

    submit.addEventListener('click', event => {
        event.preventDefault();

        request = fetch(form.action, {
            method: form.method,
            body: new FormData(form)
        });

        submit.classList.add('disabled');
        progress.style.display = 'block';

        request.then(response => {
            submit.classList.remove('disabled');
            progress.style.display = 'none';
            
            if (response.ok) {
                form.reset();
                M.toast({
                    html: gettext("Contribution sent. Thanks!")
                });
            } else if (response.status === 400) {
                M.toast({
                    html: gettext("Invalid contribution :(")
                });
            } else {
                M.toast({
                    html: gettext("An error occured while sending :(")
                });
            }
        });
    });
});
