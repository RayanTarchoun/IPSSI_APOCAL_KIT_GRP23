import LegalScaffold, { type LegalSection } from './LegalScaffold';

const SECTIONS: LegalSection[] = [
  {
    title: 'Objet',
    hint: '',
    content: "Les présentes CGU régissent l'utilisation de la plateforme EduTutor IA, service de génération de quiz pédagogiques par intelligence artificielle."
  },
  {
    title: 'Acceptation des conditions',
    hint: '',
    content: "L'utilisateur accepte les CGU lors de la création de son compte. Tout usage du service vaut acceptation des CGU en vigueur."
  },
  {
    title: 'Accès au service',
    hint: '',
    content: 'Accès par navigateur web moderne (Chrome, Firefox, Edge). Une connexion internet est requise. Le service est accessible 24h/24 sous réserve des opérations de maintenance.'
  },
  {
    title: 'Compte utilisateur',
    hint: '',
    content: "Création par email valide. L'utilisateur est responsable de la confidentialité de son mot de passe. Les informations fournies doivent être exactes et à jour."
  },
  {
    title: 'Comportements interdits',
    hint: '',
    content: 'Upload de contenu illicite, tentative de piratage, injection de prompt malveillant dans les cours, usage automatisé abusif (scraping, requêtes automatisées).'
  },
  {
    title: 'Contenu généré par IA',
    hint: '',
    content: "Les quiz sont générés par intelligence artificielle (Llama 3.2 3B via Ollama). Ils peuvent contenir des erreurs ou des hallucinations. L'enseignant doit les vérifier avant utilisation en classe. EduTutor IA ne peut être tenu responsable d'un usage inapproprié."
  },
  {
    title: 'Responsabilité',
    hint: '',
    content: "EduTutor IA est fourni \"en l'état\" à titre pédagogique dans le cadre APOCAL'IPSSI 2026. La responsabilité de l'éditeur est limitée aux dommages directs et prévisibles causés par une faute prouvée."
  },
  {
    title: 'Propriété intellectuelle',
    hint: '',
    content: "Le code source, les marques et le nom EduTutor IA appartiennent à leurs auteurs respectifs (© Mohamed EL AFRIT). L'utilisateur conserve la pleine propriété de ses cours déposés sur la plateforme."
  },
  {
    title: 'Modification des CGU',
    hint: '',
    content: "Les CGU peuvent être modifiées à tout moment. Les utilisateurs seront informés par email. L'utilisation continue du service après modification vaut acceptation des nouvelles CGU."
  },
  {
    title: 'Droit applicable et litiges',
    hint: '',
    content: 'Droit français. En cas de litige, les tribunaux compétents sont ceux du ressort de la cour d\'appel de Paris.'
  }
];

export default function CGUPage() {
  return (
    <LegalScaffold
      title="Conditions Générales d'Utilisation"
      intro="Les règles d'utilisation du service EduTutor IA, acceptées par chaque utilisateur."
      sections={SECTIONS}
      complete
    />
  );
}
