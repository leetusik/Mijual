/**
 * Per-field citation: verbatim quote + rcept_no link into the DART 원문.
 */
export interface CitationProps {
  /** The filing's rcept_no, e.g. "20260724000546" */
  rceptNo: string;
  /** Verbatim quote from the filing — never paraphrased or re-punctuated */
  quote: string;
  /** Chip label, default "근거" */
  label?: string;
  /** Start with the quote panel open */
  defaultExpanded?: boolean;
}
export declare function Citation(props: CitationProps): JSX.Element;
