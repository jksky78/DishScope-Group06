var button= document.getElementById('button')

function Vendor() {
    button.style.left = '115px'
    document.getElementById("vendor_inputs").style.display = "block";
    document.getElementById("role").value = "vendor";
}

function Student() {
    button.style.left = '0px'
    document.getElementById("vendor_inputs").style.display = "none";
    document.getElementById("role").value = "student";
}

function showPassword() {
    let password = document.getElementById("password");

    if (password.type === "password") {
        password.type = "text";
    } else {
        password.type = "password";
    }
}