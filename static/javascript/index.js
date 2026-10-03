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
const originalOrder = Array.from(dishCards);
function updateDishes() {

    const searchText = searchBar.value.toLowerCase().trim();

    const selectedFilter = filterSelect.value.toLowerCase().trim();

    const selectedSort = sortSelect.value;
    const originalOrder = Array.from(dishCards);
    console.log("Selected Dropdown Filter:", selectedFilter);
    // --------------------------------
    // FILTER
    // --------------------------------

    dishCards.forEach(function (card) {

        const dishInformation =
            card.textContent.toLowerCase();

        const cardCategory = card.dataset.category ? card.dataset.category.toLowerCase() : "";
        console.log("Card category found in HTML:", cardCategory);

        let matchesSearch =
            dishInformation.includes(searchText);


        let matchesFilter = true;


        if (selectedFilter !== "all") {

            matchesFilter =
                cardCategory.includes(selectedFilter);

        }


        // Show or hide card

        if (matchesSearch && matchesFilter) {

            card.style.display = "";

        } else {

            card.style.display = "none";

        }

    });


// --------------------------------
    // SORT (
    // --------------------------------
    // Convert NodeList to an Array so we can sort it
    const cardsArray = Array.from(dishCards);

    cardsArray.sort(function (a, b) {
        if (selectedSort === "all") {
            // Default: Put them back in their original page-load order
            return originalOrder.indexOf(a) - originalOrder.indexOf(b);
        } 
        else if (selectedSort === "priceLow") {
            return Number(a.dataset.price) - Number(b.dataset.price);
        } 
        else if (selectedSort === "priceHigh") {
            return Number(b.dataset.price) - Number(a.dataset.price);
        } 
        else if (selectedSort === "ratingLow") {
            return Number(a.dataset.rating) - Number(b.dataset.rating);
        } 
        else if (selectedSort === "ratingHigh") {
            return Number(b.dataset.rating) - Number(a.dataset.rating);
        }
        return 0;
    });

    // Put the sorted cards back into the container visually
    cardsArray.forEach(function (card) {
        dishContainer.appendChild(card);
    });
}

sortSelect.addEventListener("change", function () {
    console.log("Selected:", sortSelect.value);
    updateDishes();
});


function previewImage(event) {
    const reader = new FileReader();
    reader.onload = function() {
    const output = document.getElementById('preview');
    output.src = reader.result;
    output.style.display = 'block';
    document.getElementById('preview-text').style.display = 'none';
        };
    reader.readAsDataURL(event.target.files[0]);
        }
function clearPreview() {
    document.getElementById('preview').style.display = 'none';
    document.getElementById('preview-text').style.display = 'block';
        }


function previewImageEdit(event) {
    const input = event.target;
    const preview = document.getElementById('editImagePreview');

    // Check if a file was actually selected
    if (input.files && input.files[0]) {
        const reader = new FileReader();

        // When the file is read, change the image tag's src to the temporary local file URL
        reader.onload = function(e) {
            preview.src = e.target.result;
        }

        reader.readAsDataURL(input.files[0]);
    }
}