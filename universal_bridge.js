/**
 * 🚀 Universal Bridge - کار با هم Sunmi و هم Mars SysPro
 * 
 * این فایل رو در WebView خودتون include کنید:
 * <script src="universal_bridge.js"></script>
 */

// 🎯 Universal Print Function
function universalPrint(text) {
    console.log("🖨️ Universal Print called with:", text.substring(0, 50) + "...");
    
    if (window.android && window.android.print) {
        // Sunmi Device
        console.log("📱 Using Sunmi bridge");
        try {
            return window.android.print(text);
        } catch (e) {
            console.error("❌ Sunmi print error:", e);
            return false;
        }
    } else if (window.pywebview && window.pywebview.api && window.pywebview.api.print) {
        // Mars SysPro Universal
        console.log("🖥️ Using Mars SysPro bridge");
        try {
            window.pywebview.api.print(text);
            return true;
        } catch (e) {
            console.error("❌ Mars SysPro print error:", e);
            return false;
        }
    } else {
        console.warn("⚠️ No print bridge available");
        // Fallback - show alert
        alert("Print: " + text);
        return false;
    }
}

// 🔔 Universal Alert Function  
function universalPlayAlert() {
    console.log("🔔 Universal Play Alert called");
    
    if (window.android && window.android.playAlert) {
        // Sunmi Device
        console.log("📱 Using Sunmi alert");
        try {
            return window.android.playAlert();
        } catch (e) {
            console.error("❌ Sunmi alert error:", e);
            return false;
        }
    } else if (window.pywebview && window.pywebview.api && window.pywebview.api.playAlert) {
        // Mars SysPro Universal  
        console.log("🖥️ Using Mars SysPro alert");
        try {
            window.pywebview.api.playAlert();
            return true;
        } catch (e) {
            console.error("❌ Mars SysPro alert error:", e);
            return false;
        }
    } else {
        console.warn("⚠️ No alert bridge available");
        return false;
    }
}

// 🔇 Universal Stop Alert Function
function universalStopAlert() {
    console.log("🔇 Universal Stop Alert called");
    
    if (window.android && window.android.stopAlert) {
        // Sunmi Device
        console.log("📱 Using Sunmi stop alert");
        try {
            return window.android.stopAlert();
        } catch (e) {
            console.error("❌ Sunmi stop alert error:", e);
            return false;
        }
    } else if (window.pywebview && window.pywebview.api && window.pywebview.api.stopAlert) {
        // Mars SysPro Universal
        console.log("🖥️ Using Mars SysPro stop alert");
        try {
            window.pywebview.api.stopAlert();
            return true;
        } catch (e) {
            console.error("❌ Mars SysPro stop alert error:", e);
            return false;
        }
    } else {
        console.warn("⚠️ No stop alert bridge available");
        return false;
    }
}

// 📱 Device Detection
function getDeviceType() {
    if (window.android) {
        return 'sunmi';
    } else if (window.pywebview) {
        return 'mars_syspro';
    } else {
        return 'web';
    }
}

// 🎯 All-in-One Function برای سفارش جدید
function handleNewOrder(receiptText) {
    console.log("🎯 New Order Handler called");
    
    // 1. پخش آلارم
    universalPlayAlert();
    
    // 2. چاپ رسید (آلارم خودکار متوقف می‌شود)
    const printSuccess = universalPrint(receiptText);
    
    console.log(`📊 Order processed - Print: ${printSuccess ? 'Success' : 'Failed'}`);
    return printSuccess;
}

// 🚀 Ready Check
function isUniversalBridgeReady() {
    const deviceType = getDeviceType();
    
    switch(deviceType) {
        case 'sunmi':
            return !!(window.android && window.android.print);
        case 'mars_syspro':
            return !!(window.pywebview && window.pywebview.api);
        default:
            return false;
    }
}

// 📋 Export for modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        universalPrint,
        universalPlayAlert,
        universalStopAlert,
        handleNewOrder,
        getDeviceType,
        isUniversalBridgeReady
    };
}

// 🎉 Initialize
console.log("🚀 Universal Bridge loaded for device:", getDeviceType());
console.log("📋 Bridge ready:", isUniversalBridgeReady());

