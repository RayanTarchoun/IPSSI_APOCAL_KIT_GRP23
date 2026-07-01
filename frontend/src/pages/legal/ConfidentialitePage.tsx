import LegalScaffold, { type LegalSection } from './LegalScaffold';

const SECTIONS: LegalSection[] = [
  {
    title: 'Responsable du traitement',
    hint: '',
    content: "Équipe Groupe 23, IPSSI. Le responsable décide des finalités et des moyens du traitement des données personnelles effectué dans le cadre d'EduTutor IA."
  },
  {
    title: 'Données personnelles collectées',
    hint: '',
    content: 'Email, nom d\'utilisateur, cours déposés (PDF ou texte), quiz générés, réponses soumises, scores, historique de connexion.'
  },
  {
    title: 'Finalités du traitement',
    hint: '',
    content: 'Création et gestion du compte utilisateur, génération de quiz personnalisés, correction automatique des réponses, historique des résultats, amélioration du service.'
  },
  {
    title: 'Base légale',
    hint: '',
    content: 'RGPD Art. 6.1.a (consentement) : l\'utilisateur accepte nos conditions lors de l\'inscription. Art. 6.1.b (contrat) : données nécessaires au fonctionnement du service.'
  },
  {
    title: 'Durée de conservation',
    hint: '',
    content: 'Compte : actif + 12 mois après dernière connexion. Cours et quiz : durée de vie du compte. Logs techniques : 12 mois. Signalements : 3 ans (prescription civile).'
  },
  {
    title: 'Destinataires des données',
    hint: '',
    content: "Aucun destinataire externe. Les données restent sur le serveur local (PostgreSQL). L'équipe projet (7 membres, Groupe 23) y a accès dans le cadre du développement."
  },
  {
    title: 'Transferts hors UE',
    hint: '',
    content: "Aucun transfert hors Union européenne. Le LLM (Ollama) et la base de données fonctionnent exclusivement en local sur le serveur de l'équipe (France)."
  },
  {
    title: 'Vos droits',
    hint: '',
    content: "Accès (Art. 15), rectification (Art. 16), suppression (Art. 17), limitation (Art. 18), portabilité (Art. 20), opposition (Art. 21). Pour exercer vos droits : equipe23@ipssi.edu. Réponse sous 48h."
  },
  {
    title: 'Cookies',
    hint: '',
    content: "Voir la politique de gestion des cookies du site."
  },
  {
    title: 'Contact & réclamation',
    hint: '',
    content: "Référent données : Groupe 23 — equipe23@ipssi.edu. Droit de réclamation auprès de la CNIL (cnil.fr)."
  }
];

export default function ConfidentialitePage() {
  return (
    <LegalScaffold
      title="Politique de confidentialité"
      intro="Comment les données personnelles des utilisateurs sont collectées, utilisées et protégées (RGPD)."
      sections={SECTIONS}
      complete
    />
  );
}
