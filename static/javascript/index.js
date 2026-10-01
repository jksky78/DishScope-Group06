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

const dishContainer = document.getElementById("dishContainer");
const dishCards = Array.from(document.querySelectorAll(".dish-card"));
const filterSelect = document.getElementById("filterSelect");
const sortSelect = document.getElementById("sortSelect");

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






// Get all dish cards


// ================================
// SEARCH
// ================================

searchBar.addEventListener("input", function () {
    updateDishes();
});


// ================================
// FILTER
// ================================

filterSelect.addEventListener("change", function () {
    updateDishes();
});


// ================================
// SORT
// ================================

sortSelect.addEventListener("change", function () {
    updateDishes();
});


// ================================
// MAIN FUNCTION
// ================================

function updateDishes() {

    const searchText = searchBar.value.toLowerCase().trim();

    const selectedFilter = filterSelect.value;

    const selectedSort = sortSelect.value;


    // --------------------------------
    // FILTER
    // --------------------------------

    dishCards.forEach(function (card) {

        const dishInformation =
            card.textContent.toLowerCase();

        const category =
            card.dataset.category;


        let matchesSearch =
            dishInformation.includes(searchText);


        let matchesFilter = true;


        if (selectedFilter !== "all") {

            matchesFilter =
                category === selectedFilter;

        }


        // Show or hide card

        if (matchesSearch && matchesFilter) {

            card.style.display = "";

        } else {

            card.style.display = "none";

        }

    });


    // --------------------------------
    // SORT
    // --------------------------------


    if (selectedSort === "priceLow") {

        dishCards.sort(function (a, b) {

            return Number(a.dataset.price) -
                   Number(b.dataset.price);

        });

    }


    else if (selectedSort === "priceHigh") {

        dishCards.sort(function (a, b) {

            return Number(b.dataset.price) -
                   Number(a.dataset.price);

        });

    }


    else if (selectedSort === "ratingLow") {

        dishCards.sort(function (a, b) {

            return Number(a.dataset.rating) -
                   Number(b.dataset.rating);

        });

    }


    else if (selectedSort === "ratingHigh") {

        dishCards.sort(function (a, b) {

            return Number(b.dataset.rating) -
                   Number(a.dataset.rating);

        });

    }


    // Put cards back into the container

    dishCards.forEach(function (card) {

        dishContainer.appendChild(card);

    });

}


sortSelect.addEventListener("change", function () {
    console.log("Selected:", sortSelect.value);
    updateDishes();
});


