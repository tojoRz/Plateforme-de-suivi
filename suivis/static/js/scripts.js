$(document).ready(function() {
  $("a[data-toggle='modal']").click(function() {
    var idProjet = $(this).data("target").split("_")[2]; // Extraire l'ID du projet à partir de l'id du modal
    $.ajax({
      url: "/projet/" + idProjet, // Remplacez "/projet/" par l'URL de votre API qui retourne les données d'un projet par ID
      method: "GET",
      dataType: "json",
      success: function(data) {
        $("#voir_projet_" + idProjet + " .modal-title").text(data.type);
        $("#voir_projet_" + idProjet + " .modal-body dd:nth-of-type(1)").text(data.id);
        $("#voir_projet_" + idProjet + " .modal-body dd:nth-of-type(2)").text(data.cible);
        $("#voir_projet_" + idProjet + " .modal-body dd:nth-of-type(3)").text(data.objectif);
        $("#voir_projet_" + idProjet + " .modal-body dd:nth-of-type(4)").text(data.duree_reelle);
        $("#voir_projet_" + idProjet + " .modal-body dd:nth-of-type(5)").text(data.duree_budgetise);
        $("#voir_projet_" + idProjet + " .modal-body dd:nth-of-type(6)").text(data.date_debut_p);
        $("#voir_projet_" + idProjet + " .modal-body dd:nth-of-type(7)").text(data.date_debut_r);
        $("#voir_projet_" + idProjet + " .modal-body dd:nth-of-type(8)").text(data.date_fin_r);
        $("#voir_projet_" + idProjet + " .modal-body dd:nth-of-type(9)").text(data.observation);
      },
      error: function() {
        alert("Une erreur s'est produite lors du chargement des données du projet.");
      }
    });
  });
});

