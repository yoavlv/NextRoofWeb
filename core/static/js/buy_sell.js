document.addEventListener("DOMContentLoaded", function() {
    const buyElement = document.querySelector('.buy');
    const saleElement = document.querySelector('.sale');

    if (window.location.href.includes('asset_value')) {
        saleElement.classList.add('active');
    } else {
        buyElement.classList.add('active');
    }

    buyElement.addEventListener('click', function() {
        setActiveState(buyElement, saleElement);
    });

    saleElement.addEventListener('click', function() {
        setActiveState(saleElement, buyElement);
    });

    function setActiveState(toActivate, toDeactivate) {
        toActivate.classList.add('active');
        toDeactivate.classList.remove('active');
    }
});
