//comments are commented
// let for vars
//const is static
// undefined = taking a space in memory
// null = set memory to  0

function openForm(v) {
    document.getElementById(v).style.display = "block";
}
function submitForm(v) {
    document.getElementById(v).style.display = "none";
    document.getElementById(v).style.backgroundColor = "grey";
    alert("Thanks for submitting! Its been logged!");
}
function closeForm(v) {
    document.getElementById(v).style.display = "none";
}
if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}
