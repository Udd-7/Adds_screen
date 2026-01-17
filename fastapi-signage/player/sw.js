self.addEventListener("install", event => {
    self.skipWaiting();
});

self.addEventListener("fetch", event => {
    event.respondWith(
        caches.open("ads-cache").then(cache => {
            return cache.match(event.request).then(response => {
                return (
                    response ||
                    fetch(event.request).then(networkResponse => {
                        cache.put(event.request, networkResponse.clone());
                        return networkResponse;
                    })
                );
            });
        })
    );
});
