document.addEventListener('DOMContentLoaded', event => {
    const mobileSidebar = document.getElementById('mobile-sidebar');
    const sidebarLinks = mobileSidebar.querySelectorAll('a');

    const sidenav = M.Sidenav.init(mobileSidebar, {
        edge: 'right',
        scrollOffset: 0,
    });

    sidebarLinks.forEach(link => {
        link.addEventListener('click', _ => {
            sidenav.close();
        })
    });
});
