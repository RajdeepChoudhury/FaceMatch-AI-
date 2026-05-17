const express = require("express");
const multer = require("multer");
const path = require("path");
const fs = require("fs");
const { exec } = require("child_process");

const app = express();

// -----------------------------
// VIEW ENGINE
// -----------------------------

app.set("view engine", "ejs");

// -----------------------------
// STATIC FOLDER
// -----------------------------

app.use(express.static("public"));

// -----------------------------
// CREATE UPLOADS FOLDER
// -----------------------------

if (!fs.existsSync("uploads")) {
    fs.mkdirSync("uploads");
}

// -----------------------------
// MULTER STORAGE
// -----------------------------

const storage = multer.diskStorage({

    destination: function (req, file, cb) {
        cb(null, "uploads/");
    },

    filename: function (req, file, cb) {

        const uniqueName =
            Date.now() +
            "-" +
            Math.round(Math.random() * 1E9) +
            path.extname(file.originalname);

        cb(null, uniqueName);
    }
});

const upload = multer({
    storage: storage
});

// -----------------------------
// HOME ROUTE
// -----------------------------

app.get("/", (req, res) => {

    res.sendFile(
        path.join(__dirname, "public", "index.html")
    );

});

// -----------------------------
// UPLOAD ROUTE
// -----------------------------

app.post(
    "/upload",

    upload.fields([
        { name: "image1", maxCount: 1 },
        { name: "image2", maxCount: 1 }
    ]),

    (req, res) => {

        try {

            // -----------------------------
            // CHECK FILES
            // -----------------------------

            if (
                !req.files ||
                !req.files.image1 ||
                !req.files.image2
            ) {

                return res.send("Please upload both images");
            }

            // -----------------------------
            // IMAGE PATHS
            // -----------------------------

            const image1 =
                req.files.image1[0].path;

            const image2 =
                req.files.image2[0].path;

            // -----------------------------
            // PYTHON COMMAND
            // -----------------------------

            const command =
                `python3 face_match.py "${image1}" "${image2}"`;

            // -----------------------------
            // EXECUTE PYTHON
            // -----------------------------

            exec(command, (error, stdout, stderr) => {

                // -----------------------------
                // HANDLE PYTHON ERROR
                // -----------------------------

                if (error) {

                    console.log(error);

                    return res.send(`
                        <h1>Python Execution Failed</h1>
                        <pre>${error}</pre>
                    `);
                }

                // -----------------------------
                // HANDLE STDERR
                // -----------------------------

                if (stderr) {

                    console.log(stderr);
                }

                try {

                    // -----------------------------
                    // PARSE JSON
                    // -----------------------------

                    const result =
                        JSON.parse(stdout);

                    // -----------------------------
                    // HANDLE FACE ERRORS
                    // -----------------------------

                    if (result.error) {

                        return res.send(`
                            <h1>${result.error}</h1>
                        `);
                    }

                    // -----------------------------
                    // SHOW RESULT PAGE
                    // -----------------------------

                    res.render("result", {

                        overall:
                            result.overall_match,

                        scores:
                            result.details,

                        image:
                            result.image
                    });

                } catch (parseError) {

                    console.log(parseError);

                    console.log(stdout);

                    return res.send(`
                        <h1>Error Parsing Python Result</h1>
                        <pre>${stdout}</pre>
                    `);
                }

            });

        } catch (err) {

            console.log(err);

            res.send(`
                <h1>Server Error</h1>
                <pre>${err}</pre>
            `);
        }

    }
);

// -----------------------------
// START SERVER
// -----------------------------

const PORT = 3000;

app.listen(PORT, () => {

    console.log(`
====================================
SERVER RUNNING
http://localhost:${PORT}
====================================
    `);

});
