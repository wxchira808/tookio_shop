(() => {
  const store = document.querySelector(".tookio-store");
  if (!store) return;

  const currency = store.dataset.currency;
  const shopName = store.dataset.shop;
  const phone = (store.dataset.whatsapp || "").replace(/[^0-9]/g, "");
  const cartStorageKey = `tookio-store-cart:${store.dataset.storeSlug || shopName}`;
  const cart = new Map();
  const drawer = store.querySelector(".store-cart");
  const backdrop = store.querySelector(".cart-backdrop");
  const cartItems = store.querySelector(".cart-items");
  const emptyState = store.querySelector(".cart-empty");
  const checkout = store.querySelector(".whatsapp-checkout");
  const searchInput = store.querySelector(".store-search input");
  const noResults = store.querySelector(".store-no-results");
  const visibleProductCount = store.querySelector(".visible-product-count");
  const toast = store.querySelector(".store-toast");
  let activeGroup = "all";
  let toastTimer;

  const money = (value) => `${currency} ${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  function loadCart() {
    try {
      const savedItems = JSON.parse(window.localStorage.getItem(cartStorageKey) || "[]");
      if (!Array.isArray(savedItems)) return;
      savedItems.forEach((item) => {
        if (item?.id && item?.name && Number.isFinite(Number(item.price)) && Number(item.quantity) > 0) {
          cart.set(String(item.id), {
            id: String(item.id),
            name: String(item.name),
            price: Number(item.price),
            quantity: Math.floor(Number(item.quantity)),
            trackStock: item.trackStock === true,
            stock: Number(item.stock || 0),
          });
        }
      });
    } catch (error) {
      window.localStorage.removeItem(cartStorageKey);
    }
  }

  function saveCart() {
    try {
      window.localStorage.setItem(cartStorageKey, JSON.stringify([...cart.values()]));
    } catch (error) {
      // The cart remains usable for this page when storage is unavailable.
    }
  }

  function openCart() {
    drawer.classList.add("is-open");
    drawer.setAttribute("aria-hidden", "false");
    backdrop.hidden = false;
    store.querySelectorAll(".cart-trigger").forEach((trigger) => {
      trigger.setAttribute("aria-expanded", "true");
      trigger.setAttribute("data-state", "open");
    });
    document.body.classList.add("cart-open");
  }

  function closeCart() {
    drawer.classList.remove("is-open");
    drawer.setAttribute("aria-hidden", "true");
    backdrop.hidden = true;
    store.querySelectorAll(".cart-trigger").forEach((trigger) => {
      trigger.setAttribute("aria-expanded", "false");
      trigger.removeAttribute("data-state");
    });
    document.body.classList.remove("cart-open");
  }

  function renderCart() {
    const rows = [...cart.values()];
    const count = rows.reduce((sum, item) => sum + item.quantity, 0);
    const total = rows.reduce((sum, item) => sum + item.price * item.quantity, 0);
    store.querySelectorAll(".cart-count").forEach((badge) => { badge.textContent = count; });
    store.querySelectorAll(".floating-cart-trigger").forEach((button) => {
      button.setAttribute("aria-label", `Open cart, ${count} ${count === 1 ? "item" : "items"}`);
    });
    store.querySelector(".cart-item-label-count").textContent = count;
    store.querySelector(".cart-total").textContent = money(total);
    emptyState.hidden = rows.length > 0;
    checkout.disabled = rows.length === 0 || !phone;
    cartItems.innerHTML = rows.map((item) => `
      <div class="cart-row" data-id="${item.id}">
        <div class="cart-row-info"><strong>${escapeHtml(item.name)}</strong><span>${money(item.price)}</span></div>
        <div class="quantity-control">
          <button type="button" data-action="decrease" aria-label="Decrease ${escapeHtml(item.name)}">${icon("minus")}</button>
          <span>${item.quantity}</span>
          <button type="button" data-action="increase" aria-label="Increase ${escapeHtml(item.name)}" ${item.trackStock && item.quantity >= item.stock ? "disabled" : ""}>${icon("plus")}</button>
        </div>
      </div>`).join("");
    saveCart();
  }

  function icon(name) {
    return `<svg class="store-icon" aria-hidden="true"><use href="/assets/frappe/icons/lucide/icons.svg#icon-${name}"></use></svg>`;
  }

  function escapeHtml(value) {
    const element = document.createElement("span");
    element.textContent = value;
    return element.innerHTML;
  }

  function showToast(title, detail) {
    if (!toast) return;
    toast.querySelector("strong").textContent = title;
    toast.querySelector(".store-toast-product").textContent = detail;
    toast.hidden = false;
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => { toast.hidden = true; }, 1800);
  }

  function syncVisibleStockMetadata() {
    store.querySelectorAll(".add-to-cart").forEach((button) => {
      const item = cart.get(button.dataset.id);
      if (!item) return;
      item.trackStock = button.dataset.trackStock === "1";
      item.stock = Number(button.dataset.stock || 0);
      if (item.trackStock) {
        if (item.stock <= 0) cart.delete(item.id);
        else item.quantity = Math.min(item.quantity, Math.floor(item.stock));
      }
    });
  }

  function filterProducts() {
    const query = (searchInput?.value || "").trim().toLowerCase();
    let visible = 0;
    store.querySelectorAll(".product-card").forEach((card) => {
      const matchesGroup = activeGroup === "all" || card.dataset.group === activeGroup;
      const matchesSearch = !query || card.dataset.name.includes(query);
      card.hidden = !(matchesGroup && matchesSearch);
      if (!card.hidden) visible += 1;
    });
    if (visibleProductCount) visibleProductCount.textContent = visible;
    if (noResults) noResults.hidden = visible !== 0;
  }

  store.addEventListener("click", (event) => {
    const add = event.target.closest(".add-to-cart");
    if (add && !add.disabled) {
      const existing = cart.get(add.dataset.id);
      const trackStock = add.dataset.trackStock === "1";
      const stock = Number(add.dataset.stock || 0);
      if (trackStock && stock < 1) {
        showToast("Out of stock", "This item is not currently available");
        return;
      }
      if (trackStock && existing && existing.quantity >= stock) {
        showToast("Stock limit reached", `${stock} available`);
        return;
      }
      cart.set(add.dataset.id, {
        id: add.dataset.id,
        name: add.dataset.name,
        price: Number(add.dataset.price),
        quantity: existing ? existing.quantity + 1 : 1,
        trackStock,
        stock,
      });
      renderCart();
      showToast("Added to cart", add.dataset.name);
      return;
    }

    const quantityButton = event.target.closest(".quantity-control button");
    if (quantityButton) {
      const id = quantityButton.closest(".cart-row").dataset.id;
      const item = cart.get(id);
      if (quantityButton.dataset.action === "increase" && item.trackStock && item.quantity >= item.stock) {
        showToast("Stock limit reached", `${item.stock} available`);
        return;
      }
      item.quantity += quantityButton.dataset.action === "increase" ? 1 : -1;
      if (item.quantity <= 0) cart.delete(id);
      renderCart();
      return;
    }

    const filter = event.target.closest(".group-filter");
    if (filter) {
      activeGroup = filter.dataset.group;
      store.querySelectorAll(".group-filter").forEach((button) => {
        const active = button === filter;
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-pressed", String(active));
      });
      filterProducts();
    }
  });

  searchInput?.addEventListener("input", filterProducts);

  store.querySelectorAll(".cart-trigger").forEach((trigger) => trigger.addEventListener("click", openCart));
  store.querySelector(".cart-close")?.addEventListener("click", closeCart);
  backdrop.addEventListener("click", closeCart);

  checkout.addEventListener("click", () => {
    const rows = [...cart.values()];
    if (!rows.length || !phone) return;
    const total = rows.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const lines = rows.map((item) => `• ${item.name} × ${item.quantity} — ${money(item.price * item.quantity)}`);
    const message = [`Hello ${shopName}, I would like to order:`, "", ...lines, "", `Total: ${money(total)}`].join("\n");
    window.open(`https://wa.me/${phone}?text=${encodeURIComponent(message)}`, "_blank", "noopener");
  });

  loadCart();
  syncVisibleStockMetadata();
  renderCart();
})();
