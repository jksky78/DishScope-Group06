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