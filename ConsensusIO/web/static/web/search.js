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
    alert("Thanks for the correction!\n The models will be tweaked to perform better in the future.");
}
function closeForm(v) {
    document.getElementById(v).style.display = "none";
}
if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}
