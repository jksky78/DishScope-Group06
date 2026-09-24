var button= document.getElementById('button')

function Vendor() {
    button.style.left = '115px'
    document.getElementById("role").value = "vendor";
    const vName = document.getElementById("vendor_name_input")
    const vLocation = document.getElementById("vendor_location_input")
    const role = document.getElementById("role").value

    if (role == "vendor") {
        vName.required = true
        vLocation.required = true
        document.getElementById("vendor_inputs").style.display = "block";
    }
    else {
        vName.required = false
        vLocation.required = false 
    }
}

function Student() {
    button.style.left = '0px'
    document.getElementById("vendor_inputs").style.display = "none";
    document.getElementById("role").value = "student";
    const vName = document.getElementById("vendor_name_input")
    const vLocation = document.getElementById("vendor_location_input")
    const role = document.getElementById("role")

    if (role === "vendor") {
        vName.required = true
        vLocation.required = true
    }
    else {
        vName.required = false
        vLocation.required = false 
    }
}


function showPassword() {
    let password = document.getElementById("password");

    if (password.type === "password") {
        password.type = "text";
    } else {
        password.type = "password";
    }
}

function showPassword_New() {
    let password = document.getElementById("new_password");

    if (password.type === "password") {
        password.type = "text";
    } else {
        password.type = "password";
    }
}

function showPassword_Confirm() {
    let password = document.getElementById("confirm_password");

    if (password.type === "password") {
        password.type = "text";
    } else {
        password.type = "password";
    }
}

const searchBar = document.getElementById("searchbar");
const dishCards = document.querySelectorAll(".dish-card");

searchBar.addEventListener("input", function () {

    const searchText = searchBar.value.toLowerCase().trim();

    dishCards.forEach(function (card) {

        const dishInformation = card.textContent.toLowerCase();

        if (dishInformation.includes(searchText)) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }

    });

});