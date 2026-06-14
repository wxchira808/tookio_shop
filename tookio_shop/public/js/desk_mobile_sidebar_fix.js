(function () {
	if (typeof window === "undefined") return;

	const PATCH_FLAG = "__tookioDeskMobileSidebarFix";
	if (window[PATCH_FLAG]) return;
	window[PATCH_FLAG] = true;

	const EVENT_NAMESPACE = ".tookioDeskMobileSidebarFix";
	const TOGGLE_SELECTOR = ".sidebar-toggle-btn.navbar-brand, .navbar-brand .app-logo";
	const MOBILE_QUERY = window.matchMedia("(max-width: 767.98px)");
	let captureClickHandler = null;

	const whenDeskReady = (callback) => {
		if (document.readyState === "loading") {
			document.addEventListener("DOMContentLoaded", callback, { once: true });
			return;
		}

		callback();
	};

	const isMobileDesk = () => {
		if (typeof frappe === "undefined") return false;
		if (typeof frappe.is_mobile === "function") {
			return frappe.is_mobile();
		}

		return MOBILE_QUERY.matches;
	};

	const getSidebar = () => frappe?.app?.sidebar;

	const getWrapper = () => {
		const sidebar = getSidebar();
		if (!sidebar?.wrapper?.length) return null;
		return sidebar.wrapper;
	};

	const syncSidebarUi = () => {
		const sidebar = getSidebar();
		const wrapper = getWrapper();
		if (!sidebar || !wrapper) return;

		const overlay = wrapper.find(".overlay");
		const mainSection = $(".main-section");

		wrapper.addClass("tookio-mobile-sidebar-fix");
		if (!isMobileDesk()) {
			wrapper.removeClass("tookio-mobile-sidebar-open");
			overlay.removeClass("tookio-mobile-sidebar-overlay-active");
			overlay.attr("aria-hidden", "true");
			document.body.classList.remove("tookio-mobile-sidebar-open");
			document.body.style.overflow = "";
			mainSection.css("overflow", "");
			return;
		}

		const isExpanded = Boolean(sidebar.sidebar_expanded);
		wrapper.toggleClass("tookio-mobile-sidebar-open", isExpanded);
		overlay.toggleClass("tookio-mobile-sidebar-overlay-active", isExpanded);
		overlay.attr("aria-hidden", isExpanded ? "false" : "true");
		document.body.classList.toggle("tookio-mobile-sidebar-open", isExpanded);

		if (isExpanded) {
			sidebar.set_height();
			sidebar.prevent_scroll();
			return;
		}

		document.body.style.overflow = "";
		mainSection.css("overflow", "");
	};

	const patchSidebarMethods = () => {
		const sidebar = getSidebar();
		if (!sidebar || sidebar.__tookio_mobile_sidebar_patched) return;

		sidebar.__tookio_mobile_sidebar_patched = true;

		["open", "close", "expand_sidebar", "refresh", "set_workspace_sidebar"].forEach((methodName) => {
			if (typeof sidebar[methodName] !== "function") return;

			const original = sidebar[methodName];
			sidebar[methodName] = function (...args) {
				const result = original.apply(this, args);
				syncSidebarUi();
				return result;
			};
		});
	};

	const closeSidebar = ({ force = false } = {}) => {
		const sidebar = getSidebar();
		if (!sidebar) return;

		if (force || sidebar.sidebar_expanded) {
			sidebar.close();
			return;
		}

		syncSidebarUi();
	};

	const openSidebar = () => {
		const sidebar = getSidebar();
		if (!sidebar) return;

		sidebar.set_height();
		if (!sidebar.sidebar_expanded) {
			sidebar.open();
		} else {
			syncSidebarUi();
		}
	};

	const bindDelegatedEvents = () => {
		if (captureClickHandler) {
			document.removeEventListener("click", captureClickHandler, true);
		}

		captureClickHandler = (event) => {
			if (!isMobileDesk()) return;
			const toggleButton = event.target.closest?.(TOGGLE_SELECTOR);
			if (!toggleButton || !getSidebar()) return;

			event.preventDefault();
			event.stopPropagation();
			event.stopImmediatePropagation?.();

			if (getSidebar().sidebar_expanded) {
				closeSidebar();
			} else {
				openSidebar();
			}
		};

		document.addEventListener("click", captureClickHandler, true);

		$(document).off(`page-change${EVENT_NAMESPACE}`);
		$(document).on(`page-change${EVENT_NAMESPACE}`, () => {
			if (!isMobileDesk()) return;
			window.requestAnimationFrame(() => closeSidebar({ force: true }));
		});

		window.removeEventListener("resize", syncSidebarUi);
		window.addEventListener("resize", syncSidebarUi, { passive: true });
	};

	const install = () => {
		if (typeof frappe === "undefined") return;

		const start = () => {
			patchSidebarMethods();
			bindDelegatedEvents();
			syncSidebarUi();

			frappe.router?.on?.("change", () => {
				if (!isMobileDesk()) return;
				window.requestAnimationFrame(() => closeSidebar({ force: true }));
			});
		};

		if (frappe.app?.sidebar) {
			start();
			return;
		}

		$(document).one("app_ready", start);
	};

	whenDeskReady(install);
})();
