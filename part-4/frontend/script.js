// ================= CONFIG =================
const BASE_URL = "http://127.0.0.1:5000";

// ================= STATE =================
let currentPage = 1;
const limit = 5;
let authorCurrentPage = 1;
const authorLimit = 5;

let editingBookId = null;
let editingAuthorId = null;


let searchParams = {
    title: "",
    author: "",
    year: ""
};

let sortParams = {
    sort_by: "id",
    order: "asc"
};


// ================= DOM ELEMENTS =================
const booksTableBody = document.getElementById("booksTableBody");
const authorsTableBody = document.getElementById("authorsTableBody");

const bookTitle = document.getElementById("bookTitle");
const bookYear = document.getElementById("bookYear");
const bookIsbn = document.getElementById("bookIsbn");
const bookAuthorId = document.getElementById("bookAuthorId");
const addBookBtn = document.getElementById("addBookBtn");

const authorName = document.getElementById("authorName");
const authorBio = document.getElementById("authorBio");
const authorCity = document.getElementById("authorCity");
const addAuthorBtn = document.getElementById("addAuthorBtn");

const searchBtn = document.getElementById("searchBtn");
const clearBtn = document.getElementById("clearBtn");
const searchTitle = document.getElementById("searchTitle");
const searchAuthor = document.getElementById("searchAuthor");
const searchYear = document.getElementById("searchYear");

const prevPage = document.getElementById("prevPage");
const nextPage = document.getElementById("nextPage");

const sortBy = document.getElementById("sortBy");
const sortOrder = document.getElementById("sortOrder");


// const authorPrev = document.getElementById("authorPrev");
// const authorNext = document.getElementById("authorNext");

// ================= LOAD BOOKS =================
function loadBooks() {

    let query = `${BASE_URL}/api/books?page=${currentPage}&limit=${limit}`;
    query += `&sort_by=${sortParams.sort_by}&order=${sortParams.order}`;

    if (searchParams.title) query += `&title=${encodeURIComponent(searchParams.title)}`;
    if (searchParams.author) query += `&author=${encodeURIComponent(searchParams.author)}`;
    if (searchParams.year) query += `&year=${searchParams.year}`;

    fetch(query)
        .then(res => res.json())
        .then(data => {
            if (!data.success) return;

            booksTableBody.innerHTML = "";

            if (data.books.length === 0) {
                booksTableBody.innerHTML =
                    `<tr><td colspan="4" class="empty-state">No books found</td></tr>`;
                return;
            }

            data.books.forEach(book => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${book.title}</td>
                    <td>${book.year}</td>
                    <td>${book.author ? book.author.name : "-"}</td>
                    <td>
                        <button onclick="editBook(${book.id})">Edit</button>
                        <button onclick="deleteBook(${book.id})">Delete</button>
                    </td>
                `;
                booksTableBody.appendChild(row);
            });

            document.getElementById("pageInfo").textContent =
                `Page ${data.page} of ${data.total_pages}`;

            document.getElementById("totalBooks").textContent = data.total_items;
        })
        .catch(err => console.error("Load books error:", err));
}

// ================= STATS =================
fetch(`${BASE_URL}/api/books?limit=100`)
    .then(res => res.json())
    .then(data => {
        if (!data.success) return;
        const years = new Set(data.books.map(b => b.year));
        document.getElementById("publishedYears").textContent = years.size;
    });

fetch(`${BASE_URL}/api/author`)  //here i change to author -> authors
    .then(res => res.json())
    .then(data => {
        if (!data.success) return;
        document.getElementById("totalAuthors").textContent = data.total_items;
    });

// ================= AUTHOR DROPDOWN =================
function loadAuthorDropdown() {
    fetch(`${BASE_URL}/api/author`)
        .then(res => res.json())
        .then(data => {
            if (!data.success || !data.authors) return;

            bookAuthorId.innerHTML = `<option value="">Select Author</option>`;

            data.authors.forEach(author => {
                const option = document.createElement("option");
                option.value = author.id;
                option.textContent = `${author.name} (${author.city})`;
                bookAuthorId.appendChild(option);
            });
        })
        .catch(err => console.error("Author dropdown error:", err));
}

// // ================= AUTHORS TABLE =================
// function loadAuthorsTable() {
//     Promise.all([
//         fetch(`${BASE_URL}/api/author`).then(res => res.json()),
//         fetch(`${BASE_URL}/api/books?limit=100`).then(res => res.json())
//     ])
//     .then(([authorsData, booksData]) => {
//         if (!authorsData.success || !booksData.success) return;

//         authorsTableBody.innerHTML = "";

//         authorsData.authors.forEach(author => {
//             const count = booksData.books.filter(
//                 b => b.author && b.author.id === author.id
//             ).length;

//             const row = document.createElement("tr");
//             row.innerHTML = `
//                 <td>${author.name}</td>
//                 <td>${author.city}</td>
//                 <td>${count}</td>
//                 <td>
//                     <button onclick="editauthor(${author.id})">Edit</button>
//                     <button onclick="deleteauthor(${author.id})">Delete</button>
//                 </td>
//             `;
//             authorsTableBody.appendChild(row);
//         });

//         document.getElementById("pageInfo").textContent =
//                 `Page ${data.page} of ${data.total_pages}`;

//             document.getElementById("totalBooks").textContent = data.total_items;
//     })
//     .catch(err => console.error("Authors table error:", err));
// }


// ================= AUTHORS TABLE =================
function loadAuthorsTable() {
    Promise.all([
        fetch(`${BASE_URL}/api/author?page=${authorCurrentPage}&limit=${authorLimit}`)
            .then(res => res.json()),
        fetch(`${BASE_URL}/api/books?limit=100`)
            .then(res => res.json())
    ])
    .then(([authorsData, booksData]) => {
        if (!authorsData.success || !booksData.success) return;

        authorsTableBody.innerHTML = "";

        authorsData.authors.forEach(author => {
            const count = booksData.books.filter(
                book => book.author && book.author.id === author.id
            ).length;

            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${author.name}</td>
                <td>${author.city}</td>
                <td>${count}</td>
                <td>
                    <button onclick="editAuthor(${author.id})">Edit</button>
                    <button onclick="deleteAuthor(${author.id})">Delete</button>
                </td>
            `;
            authorsTableBody.appendChild(row);
        });

        // ✅ AUTHOR pagination UI
        document.getElementById("authorPageInfo").textContent =
            `Page ${authorsData.page} of ${authorsData.total_pages}`;

        document.getElementById("totalAuthors").textContent =
            authorsData.total_items;
    })
    .catch(err => console.error("Authors table error:", err));
}





// ================= ADD / UPDATE BOOK =================
addBookBtn.addEventListener("click", () => {

    if (!bookTitle.value || !bookYear.value || !bookAuthorId.value) {
        alert("Title, Year and Author are required");
        return;
    }

    const payload = {
        title: bookTitle.value.trim(),
        year: bookYear.value.trim(),
        isbn: bookIsbn.value.trim(),
        author_id: bookAuthorId.value.trim()
    };

    const url = editingBookId
        ? `${BASE_URL}/api/books/${editingBookId}`
        : `${BASE_URL}/api/books`;

    fetch(url, {
        method: editingBookId ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) {
            alert("Failed to save book");
            return;
        }

        // Reset form
        bookTitle.value = "";
        bookYear.value = "";
        bookIsbn.value = "";
        bookAuthorId.value = "";
        editingBookId = null;
        addBookBtn.textContent = "Add Book";

        loadBooks();
        loadAuthorsTable();
    })
    .catch(err => console.error("Add/Update book error:", err));
});

// ================= ADD / UPDATE AUTHOR =================
addAuthorBtn.addEventListener("click", () => {

    // Validation
    if (!authorName.value || !authorBio.value || !authorCity.value) {
        alert("Name, bio and city are required");
        return;
    }

    const payload = {
        name: authorName.value.trim(),
        bio: authorBio.value.trim(),
        city: authorCity.value.trim()
    };

    const url = editingAuthorId
        ? `${BASE_URL}/api/authors/${editingAuthorId}`
        : `${BASE_URL}/api/authors`;

    fetch(url, {
        method: editingAuthorId ? "PUT" : "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) {
            alert("Failed to save author");
            return;
        }

        // Reset form
        authorName.value = "";
        authorBio.value = "";
        authorCity.value = "";
        editingAuthorId = null;
        addAuthorBtn.textContent = "Add Author";

        loadAuthorDropdown();
        loadAuthorsTable();
    })
    .catch(err => console.error("Add/Update author error:", err));
});



// ================= DELETE BOOK =================
function deleteBook(id) {
    if (!confirm("Delete book?")) return;

    fetch(`${BASE_URL}/api/books/${id}`, { method: "DELETE" })
        .then(res => res.json())
        .then(() => {
            loadBooks();
            loadAuthorsTable();
        });
}

// ================= DELETE AUTHOR =================
function deleteAuthor(id) {
    if (!confirm("Delete author?")) return;

    fetch(`${BASE_URL}/api/authors/${id}`, { method: "DELETE" })
        .then(res => res.json())
        .then(() => {
            loadAuthorDropdown();
            loadAuthorsTable();
        })
        .catch(err => console.error("Delete author error:", err));
}

// ================= EDIT BOOK =================
function editBook(id) {
    fetch(`${BASE_URL}/api/books/${id}`)
    .then(res => res.json())
    .then(data => {
        if (!data.success) return;
        
        const book = data.book;
        bookTitle.value = book.title;
        bookYear.value = book.year;
        bookIsbn.value = book.isbn || "";
        bookAuthorId.value = book.author.id;
        
        editingBookId = id;
        addBookBtn.textContent = "Update Book";
    })
    .catch(err => console.error("Edit book error:", err));
}

// ================= EDIT AUTHOR =================
function editAuthor(id) {
    fetch(`${BASE_URL}/api/authors/${id}`)
        .then(res => res.json())
        .then(data => {
            if (!data.success) return;

            const author = data.author;

            // Fill form
            authorName.value = author.name;
            authorBio.value = author.bio;
            authorCity.value = author.city;

            // Set edit mode
            editingAuthorId = id;
            addAuthorBtn.textContent = "Update Author";
        })
        .catch(err => console.error("Edit author error:", err));
}


// ================= SEARCH =================
searchBtn.onclick = () => {
    searchParams.title = searchTitle.value.trim();
    searchParams.author = searchAuthor.value.trim();
    searchParams.year = searchYear.value.trim();
    currentPage = 1;
    loadBooks();
};

clearBtn.onclick = () => {
    searchParams = { title: "", author: "", year: "" };
    searchTitle.value = "";
    searchAuthor.value = "";
    searchYear.value = "";
    currentPage = 1;
    loadBooks();
};

// ================= SORTING =================
sortBy.onchange = () => {
    sortParams.sort_by = sortBy.value;
    currentPage = 1;
    loadBooks();
};

sortOrder.onchange = () => {
    sortParams.order = sortOrder.value;
    currentPage = 1;
    loadBooks();
};

// ================= PAGINATION =================
prevPage.onclick = () => {
    if (currentPage > 1) {
        currentPage--;
        loadBooks();
    }
};

nextPage.onclick = () => {
    currentPage++;
    loadBooks();
};

// ================= AUTHOR PAGINATION =================
const authorPrev = document.getElementById("authorPrev");
const authorNext = document.getElementById("authorNext");

authorPrev.onclick = () => {
    if (authorCurrentPage > 1) {
        authorCurrentPage--;
        loadAuthorsTable();
    }
};

authorNext.onclick = () => {
    authorCurrentPage++;
    loadAuthorsTable();
};

// ================= INITIAL LOAD =================
loadAuthorDropdown();
loadAuthorsTable();
loadBooks();
