const searchBar = document.getElementById("searchbar");
const filterSelect = document.getElementById("filterSelect");
const sortSelect = document.getElementById("sortSelect");

const dishContainer = document.getElementById("dishContainer");


// Get all dish cards
let dishCards = Array.from(
    document.querySelectorAll(".dish-card")
);


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