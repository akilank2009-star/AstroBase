console.log("Astrobase website loaded!");


// =========================
// AI POPUP
// =========================

const aiButton =
    document.getElementById("aiButton");

const aiPopup =
    document.getElementById("aiPopup");

const aiClose =
    document.getElementById("aiClose");


if (aiButton && aiPopup && aiClose) {

    aiButton.addEventListener("click", function() {

        aiPopup.style.display =
            "block";

    });


    aiClose.addEventListener("click", function() {

        aiPopup.style.display =
            "none";

    });

}


// =========================
// ASSESSMENT POPUP
// =========================

const assessmentButton =
    document.querySelector(".assessment button");

const assessmentPopup =
    document.getElementById("assessmentPopup");

const assessmentClose =
    document.getElementById("assessmentClose");


if (
    assessmentButton &&
    assessmentPopup &&
    assessmentClose
) {

    assessmentButton.addEventListener("click", function() {

        assessmentPopup.style.display =
            "block";

    });


    assessmentClose.addEventListener("click", function() {

        assessmentPopup.style.display =
            "none";

    });

}


// =========================
// USER LOGIN / PERSONALIZATION
// =========================

async function loadCurrentUser() {

    try {

        const response =
            await fetch(
                "http://127.0.0.1:5000/api/me",
                {
                    credentials: "include"
                }
            );


        const data =
            await response.json();


        // =========================
        // USER NOT LOGGED IN
        // =========================

        if (!data.logged_in) {

            return;

        }


        // =========================
        // CURRENT USER
        // =========================

        const user =
            data.user;


        // =========================
        // NORMALIZE USER ROLE
        // =========================

        const role =
            String(user.role || "")
                .trim()
                .toLowerCase();


        // =========================
        // DETERMINE DISPLAY NAME
        // =========================

        let displayName;


        if (role === "organisation") {

            displayName =
                user.organisation_name ||
                user.name;

        }

        else {

            displayName =
                user.username ||
                user.name;

        }


        // =========================
        // DETERMINE PROFILE LINK
        // =========================

        let profileLink;


        if (role === "organisation") {

            profileLink =
                "http://127.0.0.1:5000/organisation/profile";

        }

        else if (role === "student") {

            profileLink =
                "http://127.0.0.1:5000/myastrobase/profile";

        }


        // =========================
        // NAVBAR
        // =========================

        const nav =
            document.querySelector(
                "header nav"
            );


        if (nav) {


            // =========================
            // REMOVE OLD DYNAMIC LINKS
            // =========================

            nav.querySelectorAll(
                ".dynamic-user-link, .dynamic-saved-link, .dynamic-dashboard, .dynamic-admin-dashboard, .dynamic-logout, .dynamic-ai-link, .dynamic-assessment-link, .dynamic-report-link"
            ).forEach(
                function(link) {

                    link.remove();

                }
            );


            // =========================
            // REMOVE OLD LOGOUT LINKS
            // =========================

            nav.querySelectorAll("a").forEach(
                function(link) {

                    if (
                        link.textContent.trim() ===
                        "Logout"
                    ) {

                        link.remove();

                    }

                }
            );


            // =========================
            // FIND IMPORTANT NAV LINKS
            // =========================

            let loginLink = null;

            let joinLink = null;

            let exploreLink = null;


            nav.querySelectorAll("a").forEach(
                function(link) {

                    const text =
                        link.textContent.trim();


                    if (text === "Login") {

                        loginLink =
                            link;

                    }


                    if (text === "Join Astrobase") {

                        joinLink =
                            link;

                    }


                    if (text === "Explore") {

                        exploreLink =
                            link;

                    }

                }
            );


            // =========================
            // ADMIN NAVBAR
            // =========================

            if (role === "admin") {


                // -------------------------
                // Remove normal login
                // -------------------------

                if (loginLink) {

                    loginLink.remove();

                }


                // -------------------------
                // Remove Join Astrobase
                // -------------------------

                if (joinLink) {

                    joinLink.remove();

                }


                // -------------------------
                // Remove old admin links
                // -------------------------

                nav.querySelectorAll("a").forEach(
                    function(link) {

                        const text =
                            link.textContent.trim();


                        if (
                            text === "admin" ||
                            text === "Admin" ||
                            text === "Admin Dashboard"
                        ) {

                            link.remove();

                        }

                    }
                );


                // -------------------------
                // Create Admin Dashboard
                // -------------------------

                const dashboardLink =
                    document.createElement(
                        "a"
                    );


                dashboardLink.className =
                    "dynamic-admin-dashboard";


                dashboardLink.href =
                    "http://127.0.0.1:5000/admin/dashboard";


                dashboardLink.textContent =
                    "Admin Dashboard";


                nav.appendChild(
                    dashboardLink
                );

            }


            // =========================
            // STUDENT / ORGANISATION
            // =========================

            else {


                // -------------------------
                // Remove Login
                // -------------------------

                if (loginLink) {

                    loginLink.remove();

                }


                // -------------------------
                // Remove Join Astrobase
                // -------------------------

                if (joinLink) {

                    joinLink.remove();

                }


                // -------------------------
                // Create Profile Link
                // -------------------------

                if (profileLink) {

                    const userLink =
                        document.createElement(
                            "a"
                        );


                    userLink.className =
                        "dynamic-user-link";


                    userLink.href =
                        profileLink;


                    userLink.textContent =
                        displayName;


                    nav.appendChild(
                        userLink
                    );

                }


                // =========================
                // STUDENT FEATURES
                // =========================

                if (role === "student") {


                    // =========================
                    // STUDENT ASTROBASE AI
                    // =========================

                    const aiNavLink =
                        document.createElement(
                            "a"
                        );


                    aiNavLink.className =
                        "dynamic-ai-link";


                    aiNavLink.href =
                        "astrobase_ai.html";


                    aiNavLink.textContent =
                        "Astrobase AI";


                    if (exploreLink) {

                        nav.insertBefore(
                            aiNavLink,
                            exploreLink
                        );

                    }

                    else {

                        nav.appendChild(
                            aiNavLink
                        );

                    }


                    // =========================
                    // STUDENT ASSESSMENT
                    // =========================

                    const assessmentNavLink =
                        document.createElement(
                            "a"
                        );


                    assessmentNavLink.className =
                        "dynamic-assessment-link";


                    assessmentNavLink.href =
                        "assessment.html";


                    assessmentNavLink.textContent =
                        "Assessment";


                    if (exploreLink) {

                        nav.insertBefore(
                            assessmentNavLink,
                            exploreLink
                        );

                    }

                    else {

                        nav.appendChild(
                            assessmentNavLink
                        );

                    }


                    // =========================
                    // STUDENT REPORT
                    // =========================

                    const reportNavLink =
                        document.createElement(
                            "a"
                        );


                    reportNavLink.className =
                        "dynamic-report-link";


                    reportNavLink.href =
                        "http://127.0.0.1:5000/report";


                    reportNavLink.textContent =
                        "Report";


                    if (exploreLink) {

                        nav.insertBefore(
                            reportNavLink,
                            exploreLink
                        );

                    }

                    else {

                        nav.appendChild(
                            reportNavLink
                        );

                    }


                    // =========================
                    // STUDENT SAVED
                    // =========================

                    const savedLink =
                        document.createElement(
                            "a"
                        );


                    savedLink.className =
                        "dynamic-saved-link";


                    savedLink.href =
                        "http://127.0.0.1:5000/myastrobase/saved";


                    savedLink.textContent =
                        "Saved";


                    nav.appendChild(
                        savedLink
                    );

                }


                // =========================
                // ORGANISATION DASHBOARD
                // =========================

                if (
                    role === "organisation"
                ) {

                    const dashboardLink =
                        document.createElement(
                            "a"
                        );


                    dashboardLink.className =
                        "dynamic-dashboard";


                    dashboardLink.href =
                        "http://127.0.0.1:5000/organisation/dashboard";


                    dashboardLink.textContent =
                        "Dashboard";


                    nav.appendChild(
                        dashboardLink
                    );

                }

            }


            // =========================
            // CREATE ONE LOGOUT
            // =========================

            const logoutLink =
                document.createElement(
                    "a"
                );


            logoutLink.className =
                "dynamic-logout";


            logoutLink.href =
                "http://127.0.0.1:5000/logout";


            logoutLink.textContent =
                "Logout";


            nav.appendChild(
                logoutLink
            );

        }


        // =========================
        // PERSONALIZED SECTION
        // =========================

        const personalizedSection =
            document.getElementById(
                "personalizedSection"
            );


        if (personalizedSection) {

            if (
                role === "student" ||
                role === "organisation"
            ) {

                personalizedSection.style.display =
                    "block";

            }

            else if (
                role === "admin"
            ) {

                personalizedSection.style.display =
                    "none";

            }

        }


        // =========================
        // STUDENT HOME
        // =========================

        const studentHome =
            document.getElementById(
                "studentHome"
            );


        const organisationHome =
            document.getElementById(
                "organisationHome"
            );


        if (role === "student") {


            // -------------------------
            // Show Student section
            // -------------------------

            if (studentHome) {

                studentHome.style.display =
                    "block";

            }


            // -------------------------
            // Hide Organisation section
            // -------------------------

            if (organisationHome) {

                organisationHome.style.display =
                    "none";

            }


            // -------------------------
            // Welcome message
            // -------------------------

            const welcomeUsername =
                document.getElementById(
                    "welcomeUsername"
                );


            if (welcomeUsername) {

                welcomeUsername.textContent =
                    displayName;

            }


            // -------------------------
            // Grade
            // -------------------------

            const userGrade =
                document.getElementById(
                    "userGrade"
                );


            if (userGrade) {

                userGrade.textContent =
                    user.grade ||
                    "Not set";

            }


            // -------------------------
            // Country
            // -------------------------

            const userCountry =
                document.getElementById(
                    "userCountry"
                );


            if (userCountry) {

                userCountry.textContent =
                    user.country ||
                    "Not set";

            }


            // -------------------------
            // Interests
            // -------------------------

            const userInterests =
                document.getElementById(
                    "userInterests"
                );


            if (userInterests) {

                userInterests.textContent =
                    user.interests ||
                    "Not set";

            }


            // -------------------------
            // Career Goal
            // -------------------------

            const userCareerGoal =
                document.getElementById(
                    "userCareerGoal"
                );


            if (userCareerGoal) {

                userCareerGoal.textContent =
                    user.career_goals ||
                    "Not set";

            }

        }


        // =========================
        // ORGANISATION HOME
        // =========================

        else if (
            role === "organisation"
        ) {


            // -------------------------
            // Hide Student section
            // -------------------------

            if (studentHome) {

                studentHome.style.display =
                    "none";

            }


            // -------------------------
            // Show Organisation section
            // -------------------------

            if (organisationHome) {

                organisationHome.style.display =
                    "block";

            }


            // -------------------------
            // Organisation Name
            // -------------------------

            const organisationName =
                document.getElementById(
                    "organisationName"
                );


            if (organisationName) {

                organisationName.textContent =
                    user.organisation_name ||
                    user.name;

            }


            // -------------------------
            // Organisation Type
            // -------------------------

            const organisationType =
                document.getElementById(
                    "organisationType"
                );


            if (organisationType) {

                organisationType.textContent =
                    user.organisation_type ||
                    "Not set";

            }


            // -------------------------
            // Organisation Status
            // -------------------------

            const organisationStatus =
                document.getElementById(
                    "organisationStatus"
                );


            if (organisationStatus) {

                organisationStatus.textContent =
                    user.organisation_status ||
                    "Verified";

            }


            // -------------------------
            // Organisation Email
            // -------------------------

            const organisationEmail =
                document.getElementById(
                    "organisationEmail"
                );


            if (organisationEmail) {

                organisationEmail.textContent =
                    user.email ||
                    "Not set";

            }


            // -------------------------
            // Organisation ID
            // -------------------------

            const organisationId =
                document.getElementById(
                    "organisationId"
                );


            if (organisationId) {

                organisationId.textContent =
                    user.organisation_id ||
                    "Not set";

            }

        }


        // =========================
        // ADMIN HOME
        // =========================

        else if (
            role === "admin"
        ) {


            // -------------------------
            // Hide Student section
            // -------------------------

            if (studentHome) {

                studentHome.style.display =
                    "none";

            }


            // -------------------------
            // Hide Organisation section
            // -------------------------

            if (organisationHome) {

                organisationHome.style.display =
                    "none";

            }

        }

    }

    catch (error) {

        console.error(
            "Could not load current user:",
            error
        );

    }

}


// =========================
// LOAD USER INFORMATION
// =========================

loadCurrentUser();