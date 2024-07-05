document.addEventListener('DOMContentLoaded', function() {
    let page = 2; 
    const loadMoreButton = document.getElementById('load-more');

    loadMoreButton.addEventListener('click', function() {
        const searchQuery = document.querySelector('input[name="search_query"]').value;
        const priceFilter = document.querySelector('select[name="price_filter"]').value;

        fetch(`?page=${page}&search_query=${encodeURIComponent(searchQuery)}&price_filter=${encodeURIComponent(priceFilter)}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('events-list').insertAdjacentHTML('beforeend', data.events_html);
            if (!data.has_next) {
                loadMoreButton.style.display = 'none'; 
            }
            page++;  
        })
        .catch(error => console.error('Error:', error));
    });
});
