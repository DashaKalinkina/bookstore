
document.getElementById('place-order-btn').addEventListener('click', function() {
    const formData = new FormData(document.getElementById('customer-info-form'));

    if (!formData.get('customer_name') || !formData.get('customer_phone') || !formData.get('customer_address')) {
        alert('Пожалуйста, заполните все обязательные поля (имя, телефон и адрес)');
        return;
    }
    
  
    fetch('/place-order', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/orders';
        } else {
            alert(data.message || 'Ошибка при оформлении заказа');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при отправке данных');
    });
});