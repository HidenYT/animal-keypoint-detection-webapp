function onMouseOverNavbarDropdownItem(item) {
    for(let child of item.children) {
        child.classList.add("show");
    }
}

function onMouseLeaveNavbarDropdownItem(item) {
    for(let child of item.children) {
        child.classList.remove("show");
    }
}