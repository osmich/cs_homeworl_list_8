function accept_transfer(id) {
    location.href='/approve?accept='+id;
}

function action(id) {
    changed = 2;
    location.href='/approve?accept='+changed;
}


