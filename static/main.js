// login関連（パスワード表示、非表示切り替え）
document.addEventListener("DOMContentLoaded", function () {
  const toggleIcons = document.querySelectorAll(".toggle-icon");

  toggleIcons.forEach(function (icon) {
    icon.addEventListener("click", function () {
      const targetId = this.getAttribute("data-target");
      const input = document.getElementById(targetId);
      const isPassword = input.type === "password";
      input.type = isPassword ? "text" : "password";

      // アイコン切り替え
      this.classList.toggle("fa-eye");
      this.classList.toggle("fa-eye-slash");
    });
  });
});

//設定リンクの色変更
document.addEventListener("DOMContentLoaded", () => {
  if (window.location.pathname.includes("custom")) {
    const settingActions = document.querySelector(".setting-actions");
    const settingLink = document.querySelector(".setting-link");

    if (settingActions) {
      settingActions.style.setProperty("background-color", "#6c63ff", "important");
    }
    if (settingLink) {
      settingLink.style.setProperty("color", "#fff", "important");
    }
  }
});