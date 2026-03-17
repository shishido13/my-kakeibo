export const auth = () => {
    const rootUrl = "https://accounts.google.com/o/oauth2/v2/auth";
    const options = {
        redirect_uri: "http://localhost:5173/api/auth/callback/google", // Google Consoleと同じもの
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
        access_type: "offline",
        response_type: "code",
        prompt: "consent",
        scope: [
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
        ].join(" "),
    };

    const queryString = new URLSearchParams(options).toString();
    window.location.href = `${rootUrl}?${queryString}`;
};