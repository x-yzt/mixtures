document.addEventListener('DOMContentLoaded', event => {
    const inputs = document.querySelectorAll('#embed-settings input');
    const heightAutoInput = document.querySelector('input[name="height"][value="auto"]');
    const heightFixedInput = document.querySelector('input[name="height"][value="fixed"]');
    const heightPxInput = document.querySelector('input[name="height-px"]');
    const themeDarkInput = document.querySelector('input[name="theme"][value="dark"]');
    const themeAutoInput = document.querySelector('input[name="theme"][value="auto"]');
    const themeCustomInput = document.querySelector('input[name="theme"][value="custom"]');
    const textColorInput = document.querySelector('input[name="text-color"]');
    const code = document.getElementById('embed-code');
    const jsNotice = document.getElementById('js-notice');

    const refreshModal = () => {
        if (
            themeCustomInput.checked && !textColorInput.checkValidity()
            || heightFixedInput.checked && !heightPxInput.checkValidity()
        ) return;

        const src = new URL(code.getAttribute('data-src'));

        if (themeCustomInput.checked) {
            const textColor = textColorInput.value.replace("#", "");
            src.searchParams.append("text-color", textColor);
        }
        else if (themeDarkInput.checked) {
            src.searchParams.append("theme", "dark");
        }
        else if (themeAutoInput.checked) {
            src.searchParams.append("theme", "auto");
        }
        
        const height = heightFixedInput.checked
            ? heightPxInput.value + "px"
            : "auto"

        code.textContent =
            `<iframe src="${src.href}" style="border: none; width: 100%; height: ${height}"></iframe>`;

        jsNotice.style.display = heightAutoInput.checked ? "block" : "none";
    };

    heightPxInput.addEventListener('input', event => heightFixedInput.click());

    textColorInput.addEventListener('change', event => themeCustomInput.click());

    inputs.forEach(input => {
        input.addEventListener('change', event => refreshModal());
    });

    refreshModal();
});
