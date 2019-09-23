;;; flycheck-yaml-schemalint.el --- flycheck for schemalint -*- lexical-binding: t -*-

;;; Code:

(eval-when-compile
  (require 'pcase) ; For `pcase'
  (require 'let-alist) ; For `let-alist'
  )

(require 'flycheck) ; For `flycheck-define-checker'

(defun flycheck-yaml-schemalint:parse (output checker buffer)
  (let (errors)
    (dolist (data (flycheck-parse-json output))
      (let-alist data
        (let ((status (intern (downcase (or .status "ERROR")))))
          (push
           (flycheck-error-new-at
            (or .start.line 1)
            (or .start.chacter 1)
            status
            (concat .errortype " " .message " " .where)
            ;; :id (concat .errortype " " .start)
            :checker checker
            :buffer buffer
            :filename .filename
            )
           errors))))
    (nreverse errors)))

(flycheck-define-checker yaml-schemalint
  "A Yaml linter using schemalint

See URL `https://github.com/podhmo/schemalint'.
"
  :command ("schemalint" "--guess-schema" "--always-success" "-o" "json" source-original)
  :error-parser flycheck-yaml-schemalint:parse
  :modes yaml-mode)

(add-to-list 'flycheck-checkers 'yaml-schemalint)

(provide 'flycheck-yaml-schemalint)

;; Local Variables:
;; coding: utf-8
;; indent-tabs-mode: nil
;; End:

;;; flycheck-yaml-schemalint.el ends here
