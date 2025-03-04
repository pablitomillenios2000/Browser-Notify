self.addEventListener('push', function(event) {
    const data = event.data ? event.data.json() : { title: 'Default Title', body: 'Default Message' };
    self.registration.showNotification(data.title, {
        body: data.body,
        icon: 'https://via.placeholder.com/128' // Optional icon
    });
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(clients.openWindow('/'));
});