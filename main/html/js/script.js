// ---------------------------MOBILE MENU---------------------------

const btnMenu = document.querySelector('.btn-menu');
const menuContent = document.querySelector('.header__content');
const menuLink = document.querySelectorAll('.menu__link');

if (btnMenu != null) {
  btnMenu.addEventListener('click', function () {
    btnMenu.classList.toggle('opened');
    menuContent.classList.toggle('opened');
    lockBody('lock');
  });
}

for (link of menuLink) {
  link.addEventListener('click', () => {
    btnMenu.classList.remove('opened');
    menuContent.classList.remove('opened');
    lockBody('unlock');
  });
}

// function need for 1)mobile menu 2) popup
function lockBody(action) {
  const body = document.querySelector('body');

  if (action == 'lock') {
    body.classList.toggle('lock');
  } else if (action == 'unlock') {
    body.classList.remove('lock');
  }
}

// submenu

let subMenuItems = document.querySelectorAll('.submenu-block');

subMenuItems.forEach((el) => {
  el.addEventListener('click', (e) => {
    let element = e.target;
    let parent = element.parentElement;

    if (element.nodeName === 'SPAN') {
      if (parent.classList.contains('opened')) {
        closeAllSubMenu();
      } else {
        closeAllSubMenu();
        parent.classList.add('opened');
      }
    }
  });
});

window.addEventListener('click', (e) => {
  if (!e.target.closest('.submenu-block')) {
    closeAllSubMenu();
  }
});

function closeAllSubMenu() {
  subMenuItems.forEach((el) => el.classList.remove('opened'));
}
