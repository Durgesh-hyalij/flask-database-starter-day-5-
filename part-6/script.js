const BASE_URL = "http://127.0.0.1:5000";

// Step 1: Call Flask API
fetch("BASE_URL/")
    .then(response => response.json())   // convert response to JSON
    .then(data => {
        // Step 2: Check if API call is successful
        if (data.success) {
            displayProducts(data.products);
        }
    })
    .catch(error => {
        console.error("Error fetching products:", error);
    });


// Step 3: Function to show products in table
function displayProducts(products) {
    const tableBody = document.getElementById("productsTable");

    tableBody.innerHTML = ""; // clear old data

    products.forEach(product => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${product.id}</td>
            <td>${product.name}</td>
            <td>${product.price}</td>
        `;

        tableBody.appendChild(row);
    });
}
