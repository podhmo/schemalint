;;; flycheck-yaml-schemalint.el --- flycheck for schemalint -*- lexical-binding: t -*-

;;; Code:

(eval-when-compile
  (require 'pcase) ; For `pcase'
  (require 'let-alist) ; For `let-alist'
  )

(require 'flycheck) ; For `flycheck-define-checker'

(defun flycheck-yaml-schemalint:parse-ltsv-line (line)
  (let ((s (string-trim line))
        r)
    (dolist (pair (split-string s "\t"))
      (pcase (split-string pair ":")
        (`(,x ,y . nil) (push (cons (intern x) y) r))
        (`(,x . ,ys) (push (cons (intern x) (string-join ys ":")) r))
        (_ (error "unexpected input: %s", pair))
        )
      )
    (nreverse r)))

(defun flycheck-yaml-schemalint:parse (output checker buffer)
  (unless (string-empty-p output)
    (let (errors)
      (dolist (line (split-string output "\n"))
        (when (and line (not (string-empty-p line)) (string-prefix-p "status:" line t))
          (let-alist (flycheck-yaml-schemalint:parse-ltsv-line line)
            (let ((status (intern (downcase (or .status "ERROR")))))
              (push
               (flycheck-error-new-at
                (string-to-int (car (split-string (or .start "") "@")))
                (string-to-int (or (cadr (split-string (or .start "") "@")) "1"))
                status
                (concat .errortype " " .msg " " .where)
                ;; :id (concat .errortype " " .start)
                :checker checker
                :buffer buffer
                :filename .filename
                )
               errors)))))
      (nreverse errors))))

(flycheck-define-checker yaml-schemalint
  "A Yaml linter using schemalint

See URL `https://github.com/podhmo/schemalint'.
"
  :command ("schemalint" "--guess-schema" "--always-success" source-original)
  :error-parser flycheck-yaml-schemalint:parse
  :modes yaml-mode)

(add-to-list 'flycheck-checkers 'yaml-schemalint)

(provide 'flycheck-yaml-schemalint)

;; Local Variables:
;; coding: utf-8
;; indent-tabs-mode: nil
;; End:

;;; flycheck-yaml-schemalint.el ends here
