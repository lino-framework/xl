��    d      <  �   \      �  
   �     �     �     �     �     �     �     �     �     	      	  &   .	  %   U	  *   {	  ,   �	     �	     �	     �	     
  	   
     
     !
  	   (
     2
  !   :
     \
     i
     w
     �
  	   �
     �
  	   �
     �
     �
     �
     �
     �
     �
     �
  K   �
     B     K  +   W  	   �     �     �     �     �     �     �     �     �     �     �                     3     <     B     V     l     {     �  .   �     �  O   �  M   ,  1   z  .   �  -   �  -   	      7  A   X  ,   �     �     �       T   %  #   z  '   �  $   �     �  8     +   =  !   i     �  �   �     q     }  	   �     �     �     �  	   �     �     �     �     �  e  �     N  4   m  4   �  (   �  4         5     E     X  M   n  %   �  "   �  I     R   O  X   �  O   �  "   K  /   n  +   �     �  	   �  	   �  +   �           9  (   O     x     �     �     �     �     �          )  ;   D     �     �  1   �  %   �     �  �        �     �  �   �     }     �     �     �  >   �     "  "   8  %   [     �  	   �     �  %   �     �     �            /   1  5   a  (   �  8   �     �  Q     .   e  {   �  x     X   �  J   �  I   -  I   w  K   �  �      Y   �   ?   !  B   G!  <   �!  �   �!  K   �"  X   �"  T   1#  /   �#  �   �#  J   V$  @   �$  #   �$  �  %  "   �&     �&     �&     �&     	'     '     .'  "   B'     e'     x'     �'              P       `      J   N                         #          X       5           W   $       2   %          c   *   F   >   Y   E          7   9   I   	   _   '       S   O      V           K       (   ,         L   !       ?             d   U          ;   a              :       Q   /   6   )   ^   C               H   &   =   A   R              Z         4       0          \          b   G      +   .      8   D       <         @       
              ]       [   1      "              B   3       -   T   M    Accounting Accounting Report Accounting Reports Accounting periods Accounting report Accounts Address Administrator Analytic accounts balances Bank Statements Bank accounts Base class for all tables of products. Base class for all tables on Excerpt. Base class for tables of partner vouchers. Base table for all tables showing companies. Common accounts Common sheet items Contact persons Contacts Countries Country County Creditors Debtors Displays all rows of ExcerptType. Due invoices Excerpt Types Excerpts Fax Financial Fiscal years Functions GSM General account balances ID Invoices Journal Entries Journal groups Journals List of all Journals. Accessible via Configure ‣ Accounting
‣ Journals. Locality Match rules Mixin for journal-based tables of vouchers. Movements Organization types Organizations Paper types Partner balances Partners Payment Orders Payment terms Persons Phone Places Price factors Price rules Product Categories Products Sales Sales invoice items Sales invoice journal Sales invoices Sheet item entries Sheet items Show all the ledger movements in the database. Shows all persons. Shows partners who give us some form of credit.
Inherits from DebtorsCreditors. Shows partners who have some debt against us.
Inherits from DebtorsCreditors. The base table for all tables working on Voucher. The base table of all tables on BankStatement. The base table of all tables on JournalEntry. The base table of all tables on PaymentOrder. The choicelist of price factors. The choicelist with the trade types defined for this
application. The fiscal years available in this database. The global list of VAT areas. The global list of VAT classes. The global list of VAT columns. The global list of VAT regimes.  Each item of this list is an instance of
VatRegime. The global list of common accounts. The global list of common sheet items . The list of possible journal groups. The list of price rules. The list of voucher types available in this application. The table of all VatAccountInvoice objects. The table of all VatRule objects. The table of all countries. The table of known geographical places.
A geographical place can be a city, a town, a suburb,
a province, a lake... any named geographic entity,
except for countries because these have their own table. Trade types VAT VAT areas VAT classes VAT columns VAT regimes VAT rules Voucher types Vouchers Zip code e-mail address Project-Id-Version: lino-xl 21.3.0
Report-Msgid-Bugs-To: EMAIL@ADDRESS
PO-Revision-Date: 2021-03-07 18:55+0600
Language: bn
Language-Team: bn <LL@li.org>
Plural-Forms: nplurals=2; plural=(n != 1);
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.9.0
Last-Translator: 
X-Generator: Poedit 2.4.2
 হিসাবরক্ষণ হিসাবরক্ষণ রিপোর্ট হিসাবরক্ষন রিপোর্ট হিসাবরক্ষণ কাল হিসাবরক্ষণ রিপোর্ট হিসাব ঠিকানা পরিচালক বিশ্লেষণমূলক হিসাব ভারসাম্য ব্যাংক বিবরণী ব্যাংক হিসাব সকল প্রকার পণ্য তালিকার ছক। সকল উদ্ধৃতি সমূহের তালিকার ছক। অংশীদারদের ভাউচার এর তালিকার ছক। সকল সংস্থা সমূহের তালিকার ছক। সাধারন হিসাব প্রচলিত শীট আইটেম ব্যক্তি যোগাযোগ যোগাযোগ দেশ দেশ প্রশাসনিক বিভাগ পাওনাদার দেনাদার সকল ExcerptType - এর ছক। বকেয়া চালান উদ্ধৃতিরূপ উদ্ধৃতি ফ্যাক্স আর্থিক আর্থিক বছর কর্মরূপ জি এস এম (GSM) সাধারন হিসাব ভারসাম্য আই ডি (ID) চালান খতিয়ান লিপিভুক্তি খতিয়ান শ্রেণী খতিয়ান খতিয়ানের তালিকা। কনফিগার ‣ হিসাবরক্ষণ ‣ খতিয়ান - এর
মাধ্যমে পাওয়া সম্ভব। অঞ্চল মিলন বিধি ভাউচার সংক্রান্ত খতিয়ান সমূহের তালিকার মিক্সিন। গতিবিধি সংস্থার ধরন সংস্থা কাগজের ধরন অংশীদার হিসাব ভারসাম্য অংশীদার পরিশোধ ফরমাশ পরিশোধের সর্ত ব্যক্তি ফোন স্থান দামের প্রভাবক দামের বিধি পণ্যের ধরন পণ্য বিক্রয় পণ্য বিক্রয় চালান বিক্রয় চালান খতিয়ান বিক্রয়ের চালান শীট আইটেম লিপিভুক্তি শীট আইটেম ডেটাবেইজে খতিয়ান গতিবিধির ছক। সকল ব্যক্তিবর্গ। পাওনাদার অংশীদারদের তালিকা।
DebtorsCreditors থেকে নেয়া। দেনাদার অংশীদারদের তালিকা।
DebtorsCreditors থেকে নেয়া। ভাউচার সমূহের তালিকার প্রধান ছক। সকল BankStatement তালিকার প্রধান ছক। সকল JournalEntry তালিকার প্রধান ছক। সকল PaymentOrder তালিকার প্রধান ছক। দামের প্রভাবক গুলোর তালিকা। এই অ্যাপ্লিকেশনের অন্তর্ভুক্ত সকল প্রকার লেনদেনের তালিকা। ডেটাবেইজ এ সংরক্ষিত সকল আর্থ বছর। কর অঞ্চল সমূহের তালিকা। কর শ্রেণী সমূহের তালিকা। কর কলাম সমূহের তালিকা। পূর্ববর্তী কর আমল সমূহের তালিকা। এই তালিকার প্রত্যেকটি উপাদান VatRegime
এর instance। সাধারন হিসাব সমূহের তালিকা। প্রচলিত শীট আইটেম সমূহের তালিকা। সম্ভব্য খতিয়ান শ্রেণীর তালিকা। দাম বিধির তালিকা। এই অ্যাপ্লিকেশনের অন্তর্ভুক্ত সকল প্রকার ভাউচারের তালিকা। সকল VatAccountInvoice উপাদানের তালিকা। সকল VatRule উপাদানের তালিকা। সকল দেশের ছক। কিছু জানাশোনা ভৌগলিক স্থানের ছক।
ভৌগলিক স্থান হতে পারে শহর, গ্রাম,
এলাকা, হ্রদ... যেকোনো ধরনের ভৌগলিক বস্তু,
শুধুমাত্র দেশ ব্যতীত, কারণ দেশ সমূহের নিজস্ব ছক রয়েছে। লেনদেনের ধরন কর কর অঞ্চল কর শ্রেণী কর কলাম কর আমল কর বিধি ভাউচারের ধরন ভাউচার জিপকোড (Zip code) ইমেল ঠিকানা 