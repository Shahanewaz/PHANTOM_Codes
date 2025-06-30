# PHANTOM: Prompt-based Human Attribute Navigation for Targeted Obfuscation with Multimodal Large Language Models
This repository contains the codebase for manuscript titled "PHANTOM: Prompt-based Human Attribute Navigation for Targeted Obfuscation with Multimodal Large Language Models"

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Side-by-Side Figures</title>
  <style>
    /* Container centers the row of figures */
    .fig-container {
      text-align: center;
      margin-bottom: 1em;
    }

    /* Each figure is inline-block and centered internally */
    figure {
      display: inline-block;
      width: 40%;
      margin: 0 1em;
      vertical-align: top;
      text-align: center;    /* centers img & caption */
    }

    /* Make the images fill the width of their figure */
    figure img {
      width: 100%;
      height: auto;
      display: block;
      margin: 0 auto;
    }

    /* Caption styling, with centered text */
    figure figcaption {
      display: block;
      width: 100%;
      text-align: center;
      font-style: italic;
      margin-top: 0.5em;
    }

    /* Main caption under the whole row */
    .main-caption {
      text-align: center;
      font-style: italic;
      margin-top: 0.5em;
    }
  </style>
</head>
<body>

  <div class="fig-container">
    <figure>
      <img src="Figures/ex1.png"
           alt="Impersonation within the same gender">
      <figcaption>(a) Impersonation within the same gender</figcaption>
    </figure>

    <figure>
      <img src="Figures/ex2.png"
           alt="Impersonation with different genders">
      <figcaption>(b) Impersonation with different genders</figcaption>
    </figure>
  </div>

  <p class="main-caption">
    Figure 1. PHANTOM-generated impersonation attacks in same-gender (a) and different-gender (b) scenarios.
  </p>

</body>
</html>
